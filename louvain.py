import community
import networkx as nx

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

if __name__ == '__main__':

    data_name = "book"
    path = "network/network_" + data_name + ".txt"

    obj = Graph()
    G = obj.createGraph(path)
    # 使用 Louvain 方法寻找最佳分区
    partition = community.best_partition(G)
    
    d = {}
    for it in partition.keys():
        if partition[it] not in d:
            d[partition[it]] = [it]
        else:
            d[partition[it]].append(it)

    communitys = []
    for it in d.values():
        communitys.append(it)

    print(nx.algorithms.community.modularity(G,communitys))

    print(cal_Q(communitys,G))
