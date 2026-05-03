import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

name = 'polblogs'

file_path = 'data/community_detection_results.xlsx'
df = pd.read_excel(file_path, sheet_name=name)
LPA = df['Modularity'].iloc[0:100]
Louvain = df['Modularity'].iloc[100:200]
FLPA = df['Modularity'].iloc[200:300]
Edmot = df['Modularity'].iloc[300:400]
DualFuse_CD = df['Modularity'].iloc[400:500]
Leiden = df['Modularity'].iloc[500:510]
infomap = df['Modularity'].iloc[510:520]
CNM = df['Modularity'].iloc[520:530]
LBLD = df['Modularity'].iloc[530:540]
SSLPA = df['Modularity'].iloc[540:550]


# 绘制竖着的箱线图，避免异常值判定
plt.figure(figsize=(8, 6))  # 设置图形大小
plt.boxplot([LPA, Louvain, FLPA, infomap, CNM, LBLD, SSLPA, Edmot, DualFuse_CD], 
            labels=['LPA', 'Louvain', 'FLPA', 'infomap', 'CNM', 'LBLD', 'SSLPA', 'Edmot', 'DualFuse-CD'],  # 添加标签
            notch=True,                        # 箱体是否有缺口
            vert=True,                         # 竖着绘制箱线图
            patch_artist=True,                 # 启用箱体填充颜色
            boxprops=dict(facecolor='lightblue', color='black'),  # 箱体颜色
            whiskerprops=dict(color='black', linewidth=1.5),  # 胡须颜色和线宽
            capprops=dict(color='black', linewidth=2),  # 顶部/底部线颜色和线宽
            flierprops=dict(marker='o', markerfacecolor='red', markersize=5, linestyle='none'),
            whis=[0, 100])  # 设置whis参数为[0, 100]，扩展胡须到数据范围的最大最小值

# 显示图形
plt.title(name)  # 标题
plt.show()
