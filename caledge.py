import collections
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

if __name__ == '__main__':
    path = 'network/example2.txt'
    obj = Graph()
    G = obj.createGraph(path)
    for edge in G.edges():
        sim = cal_snn_sim_between_two_nodes(G,edge[0],edge[1])
        print(edge[0],edge[1],sim)
        # if not(sim >= 0.6 and (len(set(G[edge[0]].keys()) & set(G[edge[1]].keys()))) > 2):
        #     print(edge[0],edge[1],sim)



















# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import openpyxl

# # 使用Pandas读取TSV文件
# path = 'data/community_detection_results.xlsx'
# # data = pd.read_csv('data/data.tsv', sep='\t')
# # print(data)

# df = pd.read_excel(path,sheet_name = 'polblogs')
# column_data = df['Modularity']

# # # 生成两组随机数据
# LPA = column_data.iloc[0:100]
# Louvain = column_data.iloc[100:200]
# FLPA = column_data[200:300]
# EdMot = column_data[300:400]
# EdMot_SNN = column_data[400:500]
# Leiden = column_data[500:510]
# Infomap = column_data[510:520]
# CNM = column_data[520:530]
# CBLD = column_data[530:540]
# SSLPA = column_data[540:550]
# print("LPA",round(np.mean(LPA),4))
# print("Louvain",round(np.mean(Louvain),4))
# print("FLPA",round(np.mean(FLPA),4))
# print("Leiden",round(np.mean(Leiden),4))
# print("Infomap",round(np.mean(Infomap),4))
# print("CNM",round(np.mean(CNM),4))
# print("CBLD",round(np.mean(CBLD),4))
# print("SSLPA",round(np.mean(SSLPA),4))
# print("EdMot",round(np.mean(EdMot),4))
# print("EdMot_SNN",round(np.mean(EdMot_SNN),4))

# # # 绘制竖着的箱线图
# # plt.figure(figsize=(8, 6))  # 设置图形大小
# plt.boxplot([LPA, Louvain,FLPA,Leiden,Infomap,CNM,CBLD,SSLPA,EdMot,EdMot_SNN], 
#             labels=['LPA', 'Louvain','FLPA','Leiden','Infomap','CNM','CBLD','SSLPA','EdMot','EdMot_SNN'],  # 添加标签
#             notch=True,                        # 箱体是否有缺口
#             vert=True,                         # 竖着绘制箱线图
#             patch_artist=True,                 # 启用箱体填充颜色
#             boxprops=dict(facecolor='lightblue', color='black'),  # 箱体颜色
#             whiskerprops=dict(color='black', linewidth=1.5),  # 胡须颜色和线宽
#             capprops=dict(color='black', linewidth=2),  # 顶部/底部线颜色和线宽
#             flierprops=dict(marker='o', markerfacecolor='red', markersize=5, linestyle='none'),
#             whis=[0,100]
#             )  # 异常值样式

# # # 显示图形
# # plt.title('karate')  # 标题
# # plt.show()
