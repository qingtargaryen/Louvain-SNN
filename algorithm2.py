import collections
import random
import time
import networkx as nx
import matplotlib.pyplot as plt
import show
import edmot


def load_graph(path):
    G = collections.defaultdict(dict)
    with open(path) as text:
        for line in text:
            vertices = line.strip().split()
            v_i = int(vertices[0])
            v_j = int(vertices[1])
            w = 1.0  # 数据集有权重的话则读取数据集中的权重
            G[v_i][v_j] = w
            G[v_j][v_i] = w
    return G


def cal_snn_sim_between_two_nodes(G, node1, node2):
    """
    :param node1: 节点1
    :param node2: 节点2
    :return: 相似度
    """
    sim_1 = (len(set(G[node1].keys()) & set(G[node2].keys())) + 1) / (len(set(G[node1].keys())) + 1)
    sim_2 = (len(set(G[node1].keys()) & set(G[node2].keys())) + 1) / (len(set(G[node2].keys())) + 1)
    sim = sim_1 if sim_1 < sim_2 else sim_2
    return sim


# 节点类 存储社区与节点编号信息
class Vertex:
    def __init__(self, vid, cid, nodes, k_in=0):
        # 节点编号
        self._vid = vid
        # 社区编号
        self._cid = cid
        self._nodes = nodes
        self._kin = k_in  # 结点内部的边的权重


class Louvain:
    def __init__(self, G, G1, SIM_Thread=None):
        self.SIM_Thread = SIM_Thread  # snn的阈值 以提起高相似性的边形成核心社区
        self.G1 = G1
        self._G = G
        self._m = 0  # 边数量 图会凝聚动态变化
        self._cid_vertices = {}  # 需维护的关于社区的信息(社区编号,其中包含的结点编号的集合)
        self._vid_vertex = {}  # 需维护的关于结点的信息(结点编号，相应的Vertex实例)
        for vid in self._G.keys():
            # 刚开始每个点作为一个社区
            self._cid_vertices[vid] = {vid}
            # 刚开始社区编号就是节点编号
            self._vid_vertex[vid] = Vertex(vid, vid, {vid})
            # 计算边数  每两个点维护一条边
            self._m += sum([1 for neighbor in self._G[vid].keys() if neighbor > vid])

    def generator_communities_by_snn(self):
        """
        利用SNN生成初始社区
        :param SIM_Thread: 阈值
        :return:
        """
        communities = []
        for n1 in self._G:
            for n2 in self._G[n1]:
                if n1 >= n2:
                    continue
                # sim = cal_snn_sim_between_two_nodes(self._G, n1, n2)
                if cal_snn_sim_between_two_nodes(self.G1, n1, n2) >= self.SIM_Thread:
                    # Use a set to avoid duplicate nodes
                    new_community = {n1, n2}
                    merged = False
                    # Check if the new community intersects with any existing community
                    for i, community in enumerate(communities):
                        if new_community & community:  # Merge if they intersect
                            communities[i] = community | new_community
                            merged = True
                            break
                    if not merged:
                        communities.append(new_community)
        # Final merge of communities to ensure independence
        final_communities = []
        for community in communities:
            for i, final_community in enumerate(final_communities):
                if community & final_community:  # Merge if they intersect
                    final_communities[i] = final_community | community
                    break
            else:
                final_communities.append(community)
        return final_communities

    def Optimized(self, communities):
        """
        优化snn获得的初始社区，将边缘节点集进行优化，合并到其邻居社区里面
        :param communities:
        :return:
        """
        nodes_to_move = set()
        signed_nodes = {node: index for index, community in enumerate(communities) for node in community}
        unsigned_nodes = set(self.G1.nodes()) - set(signed_nodes.keys())
        for un in list(unsigned_nodes):
            if un not in unsigned_nodes:
                continue
            c = set()
            nodes = {un}
            while True:
                flag = True
                un_neighbors = set(v for n in nodes for v in self._G[n].keys() if v not in nodes)
                for unn in un_neighbors:
                    if len(c) > 1:
                        break
                    if unn in signed_nodes.keys():
                        c.add(signed_nodes[unn])
                    else:
                        if unn not in nodes:
                            nodes.add(unn)
                            flag = False
                if len(c) > 1:
                    break
                if flag:
                    break
            if len(c) == 1:
                index = c.pop()
                for n in nodes:
                    communities[index].add(n)
                    unsigned_nodes.remove(n)
                    nodes_to_move.add(n)
        return communities

    def origin_communities(self, communities):
        """
        对snn获得的初始社区转换成louvain能运行的格式，即改变节点的信息类
        :param communities:
        :return:
        """
        for index, community in enumerate(communities):
            for node in community:
                # 将每一个初始社区第一个节点的cid确定为这个社区的cid
                cid = self._vid_vertex[community[0]]._cid
                if node == community[0]:
                    # 如果是第一个节点就不做处理，本身就在这个cid里面
                    continue
                # 获得节点的cid
                v_cid = self._vid_vertex[node]._cid
                # 获得节点的编号
                v_vid = self._vid_vertex[node]._vid
                # 让该节点的社区编号变为取得最大增益邻居节点的编号
                self._vid_vertex[v_vid]._cid = cid
                # 在该社区编号下添加该节点
                self._cid_vertices[cid].add(v_vid)
                # 以前的社区中去除该节点
                self._cid_vertices[v_cid].remove(v_vid)
        # 进行节点压缩，保持不变性
        self.second_stage()

    # 模块度优化阶段
    def first_stage(self):
        mod_inc = False  # 用于判断算法是否可终止
        visit_sequence = list(self._G.keys())
        # 随机访问
        random.shuffle(visit_sequence)
        while True:
            can_stop = True  # 第一阶段是否可终止
            # 遍历所有节点
            for v_vid in visit_sequence:
                # 获得节点的社区编号
                v_cid = self._vid_vertex[v_vid]._cid
                # k_v节点的权重(度数)  内部与外部边权重之和
                k_v = sum(self._G[v_vid].values()) + \
                      self._vid_vertex[v_vid]._kin
                # 存储模块度增益大于0的社区编号
                cid_Q = {}
                # 遍历节点的邻居
                for w_vid in self._G[v_vid].keys():
                    # 获得该邻居的社区编号
                    w_cid = self._vid_vertex[w_vid]._cid
                    if w_cid in cid_Q:
                        continue
                    else:
                        # tot是关联到社区C中的节点的链路上的权重的总和
                        tot = sum(
                            [sum(self._G[k].values()) + self._vid_vertex[k]._kin for k in self._cid_vertices[w_cid]])
                        if w_cid == v_cid:
                            tot -= k_v
                        # k_v_in是从节点i连接到C中的节点的链路的总和
                        k_v_in = sum(
                            [v for k, v in self._G[v_vid].items() if k in self._cid_vertices[w_cid]])
                        # 由于只需要知道delta_Q的正负，所以少乘了1/(2*self._m)
                        delta_Q = 2 * k_v_in - k_v * tot / self._m
                        cid_Q[w_cid] = delta_Q
                # 取得最大增益的编号
                cid, max_delta_Q = sorted(
                    cid_Q.items(), key=lambda item: item[1], reverse=True)[0]
                if max_delta_Q > 0.0 and cid != v_cid:
                    # 让该节点的社区编号变为取得最大增益邻居节点的编号
                    self._vid_vertex[v_vid]._cid = cid
                    # 在该社区编号下添加该节点
                    self._cid_vertices[cid].add(v_vid)
                    # 以前的社区中去除该节点
                    self._cid_vertices[v_cid].remove(v_vid)
                    # 模块度还能增加 继续迭代
                    can_stop = False
                    mod_inc = True
            if can_stop:
                break
        return mod_inc

    # 网络凝聚阶段
    def second_stage(self):
        cid_vertices = {}
        vid_vertex = {}
        # 遍历社区和社区内的节点
        for cid, vertices in self._cid_vertices.items():
            if len(vertices) == 0:
                continue
            new_vertex = Vertex(cid, cid, set())
            # 将该社区内的所有点看做一个点
            for vid in vertices:
                new_vertex._nodes.update(self._vid_vertex[vid]._nodes)
                new_vertex._kin += self._vid_vertex[vid]._kin
                # k,v为邻居和它们之间边的权重 计算kin社区内部总权重 这里遍历vid的每一个在社区内的邻居
                # 因为边被两点共享后面还会计算  所以权重/2
                for k, v in self._G[vid].items():
                    if k in vertices:
                        new_vertex._kin += v
            # 新的社区与节点编号
            cid_vertices[cid] = {cid}
            vid_vertex[cid] = new_vertex

        G = collections.defaultdict(dict)
        # 遍历现在不为空的社区编号 求社区之间边的权重
        for cid1, vertices1 in self._cid_vertices.items():
            if len(vertices1) == 0:
                continue
            for cid2, vertices2 in self._cid_vertices.items():
                # 找到cid后另一个不为空的社区
                if cid2 <= cid1 or len(vertices2) == 0:
                    continue
                edge_weight = 0.0
                # 遍历 cid1社区中的点
                for vid in vertices1:
                    # 遍历该点在社区2的邻居已经之间边的权重(即两个社区之间边的总权重  将多条边看做一条边)
                    for k, v in self._G[vid].items():
                        if k in vertices2:
                            edge_weight += v
                if edge_weight != 0:
                    G[cid1][cid2] = edge_weight
                    G[cid2][cid1] = edge_weight
        # 更新社区和点 每个社区看做一个点
        self._cid_vertices = cid_vertices
        self._vid_vertex = vid_vertex
        self._G = G

    def get_communities(self):
        communities = []
        for vertices in self._cid_vertices.values():
            if len(vertices) != 0:
                c = set()
                for vid in vertices:
                    c.update(self._vid_vertex[vid]._nodes)
                communities.append(list(c))
        return communities

    def execute_by_snn(self):
        c = self.Optimized(self.generator_communities_by_snn())
        # 对获得的初始社区进行约束，要求每个社区内的节点大于3个
        communities = [list(cc) for cc in c if len(cc) > 3]
        # 获得初始社区，这里面的节点是不动的所以可以之接用Louvain阶段二凝聚超级节点
        self.origin_communities(communities)
        while True:
            # 反复迭代，直到网络中任何节点的移动都不能再改善总的 modularity 值为止
            mod_inc = self.first_stage()
            if mod_inc:
                self.second_stage()
            else:
                break
        return self.get_communities()

    def execute(self):
        while True:
            # 反复迭代，直到网络中任何节点的移动都不能再改善总的 modularity 值为止
            mod_inc = self.first_stage()
            if mod_inc:
                self.second_stage()
            else:
                break
        return self.get_communities()


def cal_Q(partition, G):  # 计算Q
    # 如果为真，则返回3元组（u、v、ddict）中的边缘属性dict。如果为false，则返回2元组（u，v）
    m = len(G.edges(None, False))
    # print(G.edges(None,False))
    # print("=======6666666")
    a = []
    e = []
    for community in partition:  # 把每一个联通子图拿出来
        t = 0.0
        for node in community:  # 找出联通子图的每一个顶点
            # G.neighbors(node)找node节点的邻接节点
            t += len([x for x in G.neighbors(node)])
        a.append(t / (2 * m))
    #             self.zidian[t/(2*m)]=community
    for community in partition:
        t = 0.0
        for i in range(len(community)):
            for j in range(len(community)):
                if G.has_edge(community[i], community[j]):
                    t += 1.0
        e.append(t / (2 * m))

    q = 0.0
    for ei, ai in zip(e, a):
        q += (ei - ai ** 2)
    return q


class Graph:

    def __init__(self):
        self.graph = nx.Graph()

    def createGraph(self, filename):
        file = open(filename, 'r')

        for line in file.readlines():
            nodes = line.split()
            edge = (int(nodes[0]), int(nodes[1]))
            self.graph.add_edge(*edge)

        return self.graph


def get_mean_time_max_q_by_SNN(path, max_q, SIM_Thread):
    """
    SNN加强Louvain后运行10次获得一个数据集的平均运行时间
    :param path:
    :return:
    """
    times = 0
    all_time = 0
    for i in range(10):
        G = load_graph(path)
        obj = Graph()
        G1 = obj.createGraph(path)
        all_cost = 0
        iter_time = 0
        while True:
            """迭代找最优解"""
            iter_time += 1
            start_time = time.time()
            algorithm = Louvain(G, G1, SIM_Thread)
            communities = algorithm.execute_by_snn()
            end_time = time.time()
            cost = end_time - start_time
            all_cost += cost
            if round(cal_Q(communities, G1), 4) >= max_q:
                print(round(cal_Q(communities, G1), 4))
                break
        times += all_cost
        all_time += iter_time
        print("迭代了多少次:", iter_time)
        print("第", i + 1, "次找到最优解的运行时间为：", all_cost)
    print("平均运行时间为：", times / 10)
    print("平均迭代次数为：：", all_time / 10)

def get_max_q(path):
    """
    运行100次获得一个数据集的最大模块度
    :param path:
    :return: max_q
    """
    max_q = 0
    for i in range(100):
        G = load_graph(path)
        obj = Graph()
        G1 = obj.createGraph(path)
        algorithm = Louvain(G, G1)
        communities = algorithm.execute()
        if cal_Q(communities, G1) > max_q:
            max_q = cal_Q(communities, G1)
    return max_q


def get_mean_time_max_q(path, max_q):
    """
    Louvain运行10次获得一个数据集的平均运行时间
    :param path:
    :param max_q:
    :return:
    """
    times = 0
    all_time = 0
    for i in range(10):
        G = load_graph(path)
        obj = Graph()
        G1 = obj.createGraph(path)
        all_cost = 0
        iter_time = 0
        while True:
            iter_time += 1
            start_time = time.time()
            algorithm = Louvain(G, G1)
            communities = algorithm.execute()
            end_time = time.time()
            cost = end_time - start_time
            all_cost += cost
            if round(cal_Q(communities, G1), 4) >= max_q:
                print(round(cal_Q(communities, G1), 4))
                break
        times += all_cost
        all_time += iter_time
        print("迭代了多少次:", iter_time)
        print("第", i + 1, "次找到最优解的运行时间为：", all_cost)
    print("平均运行时间为：", times / 10)
    print("平均迭代次数为：：", all_time / 10)


if __name__ == '__main__':
    # example_data = ["karate", "dolphins", "football", "polblogs", "polbooks","email"]
    SIM_Thread = 0.4  # 对于阈值的设置，在email数据集中要将阈值设置为0.6，其余0.4
    data_name = "dolphin"
    path = "network/network_" + data_name + ".txt"

    """单独运行Louvain"""
    # G = load_graph(path)
    # obj = Graph()
    # G1 = obj.createGraph(path)
    # algorithm = Louvain(G, G1, SIM_Thread)
    # communities = algorithm.execute_by_snn()
    # print(cal_Q(communities, G1))

    max_q = get_max_q(path)
    max_q = round(max_q, 4)  # 保留4位小数
    print(data_name, "运行100次得到的最大模块度:", max_q)
    print("Louvain算法：")
    get_mean_time_max_q(path, max_q)  # louvain的迭代过程
    print("===============================")
    print("Louvain_SNN算法：")
    get_mean_time_max_q_by_SNN(path, max_q, SIM_Thread)  # louvain_SNN的迭代过程
