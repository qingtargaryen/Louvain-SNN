import collections
import random
import time
import networkx as nx
import matplotlib.pyplot as plt
import sys
import show
import edmot
import openpyxl
import pandas as pd


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
    # # 获取节点的邻居集合
    # neighbors_i = set(G[node1].keys())
    # neighbors_j = set(G[node2].keys())

    # # 计算 N(i)-{j} 和 N(j)-{i}
    # neighbors_i_without_j = neighbors_i - {node2}
    # neighbors_j_without_i = neighbors_j - {node1}
    # snn_neighbors = neighbors_i_without_j & neighbors_j_without_i

    # sim_1 = len(snn_neighbors) / len(neighbors_i_without_j) if neighbors_i_without_j else 0
    # sim_2 = len(snn_neighbors) / len(neighbors_j_without_i) if neighbors_j_without_i else 0

    sim_1 = (len(set(G[node1].keys()) & set(G[node2].keys())) + 1) / (len(set(G[node1].keys())) + 1)
    sim_2 = (len(set(G[node1].keys()) & set(G[node2].keys())) + 1) / (len(set(G[node2].keys())) + 1)
    sim = sim_1 if sim_1 < sim_2 else sim_2
    # sim = (sim_1 + sim_2) / 2
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
    def __init__(self, G, G1, starttime , SIM_Thread=None):
        self.SIM_Thread = SIM_Thread  # snn的阈值 以提起高相似性的边形成核心社区
        self.G1 = G1
        self._G = G
        self._m = 0  # 边数量 图会凝聚动态变化
        self._cid_vertices = {}  # 需维护的关于社区的信息(社区编号,其中包含的结点编号的集合)
        self._vid_vertex = {}  # 需维护的关于结点的信息(结点编号，相应的Vertex实例)
        self.midtime = starttime
        for vid in self._G.keys():
            # 刚开始每个点作为一个社区
            self._cid_vertices[vid] = {vid}
            # 刚开始社区编号就是节点编号
            self._vid_vertex[vid] = Vertex(vid, vid, {vid})
            # 计算边数  每两个点维护一条边
            self._m += sum([1 for neighbor in self._G[vid].keys() if neighbor > vid])

    def _overlap(self, node_1, node_2):
        """
        Calculating the neighbourhood overlap for a pair of nodes.
        :param node_1: Source node 1.
        :param node_2: Source node 2.
        :return neighbourhood overlap: Overlap score.
        """
        nodes_1 = self.G1.neighbors(node_1)
        nodes_2 = self.G1.neighbors(node_2)
        return len(set(nodes_1).intersection(set(nodes_2)))

    def generator_communities_by_snn(self):
        """
        利用SNN生成初始社区
        :param SIM_Thread: 阈值
        :return:
        """
        communities = []
        mp = {}        
        for n in self._G:
            mp[n] = []
        for n1 in self._G:
            for n2 in self._G[n1]:
                if n1 >= n2:
                    continue
                # sim = cal_snn_sim_between_two_nodes(self._G, n1, n2)
                sim = cal_snn_sim_between_two_nodes(self.G1, n1, n2)
                mp[n1].append((sim,n2))
                mp[n2].append((sim,n1))

        for n in self._G:
            mp[n] = sorted(mp[n],key=lambda s : s[0],reverse=True)
        
        G1 = nx.Graph()
        for n in self._G:
            for idx,it in enumerate(mp[n]):
                # sim = cal_snn_sim_between_two_nodes(self._G, n1, n2)
                # Use a set to avoid duplicate nodes
                if idx < 5:
                    G1.add_edge(n,it[1])

        edges = []
        noedges = []
        for n1 in G1:
            for n2 in G1[n1]:
                if n1 >= n2:
                    continue
                sim = cal_snn_sim_between_two_nodes(G1, n1, n2)
                if sim >= 0.61 and self._overlap(n1,n2) > 2:
                    # Use a set to avoid duplicate nodes
                    edges.append((n1,n2))
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
                else:
                    noedges.append((n1,n2))

        self.motif_graph = nx.from_edgelist(edges)
        components = [c for c in nx.connected_components(self.motif_graph)]
        components = [[len(c), c] for c in components]
        components.sort(key=lambda x: x[0], reverse=True)
        important_components = [components[comp][1] for comp
                                in range(len(components))]
        self.blocks = [list(graph) for graph in important_components if len(graph) >= len(list(important_components[0])) // 2]
        new_edges = [(n_1, n_2) for nodes in self.blocks for n_1 in nodes for n_2 in nodes if n_1!= n_2]
        self.G1.add_edges_from(new_edges)
        G1.add_edges_from(new_edges)
        for e in new_edges:
            if e[0] not in self._G or e[1] not in self._G[e[0]]:
                self._G[e[0]][e[1]] = 1
                self._G[e[1]][e[0]] = 1

        for n1,n2 in noedges:
            sim = cal_snn_sim_between_two_nodes(G1, n1, n2)
            if sim >= self.SIM_Thread:
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
        # communities = sorted(communities, key=lambda b: -len(b))  # 按社区大小排序
        # count = 0
        # for communitie in communities:
        #     count += 1
        #     print("社区", count, " ", communitie)
        # 获得初始社区，这里面的节点是不动的所以可以之接用Louvain阶段二凝聚超级节点
        # exit(0)
        self.origin_communities(communities)

        self.midtime = time.time()

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

# 可视化划分结果
def showCommunity(G, partition, pos):
    # 划分在同一个社区的用一个符号表示，不同社区之间的边用黑色粗体
    cluster = {}
    labels = {}
    for index, item in enumerate(partition):
        for nodeID in item:
            labels[nodeID] = r'$' + str(nodeID) + '$'  # 设置可视化label
            cluster[nodeID] = index  # 节点分区号

    # 可视化节点
    colors = ['r', 'g', 'b', 'y', 'm'] * 100
    shapes = ['v', 'D', 'o', '^', '<'] * 100
    for index, item in enumerate(partition):
        nx.draw_networkx_nodes(G, pos, nodelist=item,
                               node_color=colors[index],
                               node_shape=shapes[index],
                               node_size=350,
                               alpha=1)

    # 可视化边
    edges = {len(partition): []}
    for link in G.edges():
        # cluster间的link
        if cluster[link[0]] != cluster[link[1]]:
            edges[len(partition)].append(link)
        else:
            # cluster内的link
            if cluster[link[0]] not in edges:
                edges[cluster[link[0]]] = [link]
            else:
                edges[cluster[link[0]]].append(link)

    for index, edgelist in enumerate(edges.values()):
        # cluster内
        if index < len(partition):
            nx.draw_networkx_edges(G, pos,
                                   edgelist=edgelist,
                                   width=1, alpha=0.8, edge_color=colors[index])
        else:
            # cluster间
            nx.draw_networkx_edges(G, pos,
                                   edgelist=edgelist,
                                   width=3, alpha=0.8, edge_color=colors[index])

    # 可视化label
    nx.draw_networkx_labels(G, pos, labels, font_size=12)

    plt.axis('off')
    plt.show()

def get_mean_time_max_q_by_SNN(path, SIM_Thread):
    """
    SNN加强Louvain后运行10次获得一个数据集的平均运行时间
    :param path:
    :return:
    """
    times = 0
    all_time = 0

    G = load_graph(path)
    obj = Graph()
    G1 = obj.createGraph(path)
    pos = nx.kamada_kawai_layout(G1) # 点的位置
    obj2 = Graph()
    G2 = obj2.createGraph(path)

    all_cost = 0
    iter_time = 0
    mp = {}
    avg = 0

    qian_all_cost = 0
    hou_all_cost = 0

    # dpath = 'data/EdMot_SNN.xlsx'
    # run = []
    # m = []
    # t = []

    while iter_time < 100:
        """迭代找最优解"""
        iter_time += 1
        # print(iter_time)
        start_time = time.time()
        algorithm = Louvain(G, G1, start_time, SIM_Thread)
        communities = algorithm.execute_by_snn()
        end_time = time.time()
        cost = end_time - start_time
        all_cost += cost
        zhi = round(cal_Q(communities, G2), 4)
        avg += zhi

        qian_cost = algorithm.midtime - start_time
        hou_cost = end_time - algorithm.midtime

        qian_all_cost += qian_cost
        hou_all_cost += hou_cost

        # run.append(iter_time)
        # m.append(zhi)
        # t.append(round(cost,4))

        # print(zhi)
        # # exit(0)
        # # # 显示
        # communities = sorted(communities, key=lambda b: -len(b))  # 按社区大小排序
        # count = 0
        # for communitie in communities:
        #     count += 1
        #     print("社区", count, " ", communitie)
        # showCommunity(G1, communities, pos)
        # break

        if zhi in mp:
            mp[zhi] += 1
        else:
            mp[zhi] = 1
    
    # data = {'run':run,'m':m,'t':t}
    # df = pd.DataFrame(data)
    # df.to_excel(dpath)

    for it in sorted(mp):
        print((it,mp[it]))
    print("平均模块度:",round(avg / 100,4))
    print("平均时间:",round(all_cost / 100,4))
    print("平均预处理时间:",round(qian_all_cost / 100,4))
    print("Louvain算法平均时间:",round(hou_all_cost / 100,4))
    times += all_cost
    all_time += iter_time

def get_mean_time_max_q(path, op):
    """
    Louvain运行10次获得一个数据集的平均运行时间
    :param path:
    :param max_q:
    :return:
    """
    times = 0
    all_time = 0

    G = load_graph(path)
    obj = Graph()
    G1 = obj.createGraph(path)
    pos = nx.kamada_kawai_layout(G1) # 点的位置
    obj2 = Graph()
    G2 = obj2.createGraph(path)
    
    ccnt = len(G.keys())
    cutoff = G1.number_of_edges()
    if cutoff < 200:
        cutoff = 3
    elif cutoff < 10000:
        cutoff = 6
    else:
        cutoff = 500

    if op:
        edm = edmot.EdMot(G1,ccnt // 50 + 1,cutoff)
        edmot_G1 = edm.fit()
        for e in edmot_G1.edges():
            # print(e)
            if e[0] not in G or e[1] not in G[e[0]]:
                G[e[0]][e[1]] = 1
                G[e[1]][e[0]] = 1

    all_cost = 0
    iter_time = 0
    mp = {}
    avg = 0

    # dpath = 'data/EdMot.xlsx'
    # run = []
    # m = []
    # t = []

    while iter_time < 100:
        iter_time += 1
        # print(iter_time)
        start_time = time.time()
        if op:
            algorithm = Louvain(G, edmot_G1)
        else:
            algorithm = Louvain(G, G1)
        communities = algorithm.execute()
        end_time = time.time()
        cost = end_time - start_time
        all_cost += cost
        zhi = round(cal_Q(communities, G2), 4)
        avg += zhi
        
        # run.append(iter_time)
        # m.append(zhi)
        # t.append(round(cost,4))

        # print(zhi)
        # # 显示
        # communities = sorted(communities, key=lambda b: -len(b))  # 按社区大小排序
        # count = 0
        # for communitie in communities:
        #     count += 1
        #     print("社区", count, " ", communitie)
        # showCommunity(G1, communities, pos)
        # break

        if zhi in mp:
            mp[zhi] += 1
        else:
            mp[zhi] = 1

    # data = {'run':run,'m':m,'t':t}
    # df = pd.DataFrame(data)
    # df.to_excel(dpath)

    for it in sorted(mp):
        print((it,mp[it]))
    print("平均模块度:",round(avg / 100,4))
    print("平均时间:",round(all_cost / 100,4))

    times += all_cost
    all_time += iter_time


if __name__ == '__main__':
    # example_data = ["karate", "dolphins", "football", "polblogs", "polbooks","email"]
    SIM_Thread = 0.41 # 对于阈值的设置，在email数据集中要将阈值设置为0.6，其余0.4
    data_name = "OpenFlights"
    path = "network/network_" + data_name + ".txt"
    # path = 'network/network.dat'

    # print("Louvain算法：")
    # get_mean_time_max_q(path, False)  # louvain的迭代过程
    # print("===============================")
    # print("Louvain_EdMot算法：")
    # get_mean_time_max_q(path, True)  # louvain的迭代过程
    # print("===============================")
    # print("Louvain_SNN算法：")
    # get_mean_time_max_q_by_SNN(path, False, SIM_Thread)  # louvain_SNN的迭代过程
    # print("===============================")
    print("Louvain_SNN_EdMot算法：")
    get_mean_time_max_q_by_SNN(path, SIM_Thread)  # louvain_SNN的迭代过程
