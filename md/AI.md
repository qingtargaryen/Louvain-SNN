我有一篇论文，设计了一个社区发现算法，大致分为三步
第一步，计算图中每条边的相似度，对于每一个点，保留相似度最大的五条边，得到一个新图。
第二步，将第一步中的新图中的每条边重新计算相似度，然后制作两张图，
第一张图是保留相似度大于等于0.4的边，这张图的连通块作为预处理的社区。
第二张图是保留相似度大于等于0.6且共同邻居数大于2的边，对于这张图所有节点数大于等于最大连通块节点数一半的连通块，将其所有点两两连边，加边成团，这张图是作为加边的图。
第三步，将原图中的节点按预处理社区图的结果预处理社区，且将加边图中所有原图中没有的边加到原图上，这样就得到了louvain算法的一个中间结果，将这个结果输入到luovain算法中继续运行得到最终的社区划分结果

相似度公式如下：
$$\mathrm{Sim~}=\mathrm{~min~}(\frac{|N_\mathrm{u}\cap N_\mathrm{v}|+1}{|N_\mathrm{u}|+1},\frac{|N_\mathrm{u}\cap N_\mathrm{v}|+1}{|N_\mathrm{v}|+1})$$
其中$N_u$表示节点$u$的邻居节点,$N_v$表示节点$v$的邻居节点

将这三步分别取名，其中第二步中的两张图的制作过程也分别取名，第一步中的新图，第二步中的两张图片的名字也要取名



针对复杂网络中枢纽节点(hub nodes)过度连接导致的社区结构模糊问题,本研究提出基于局部拓扑特征的Top-K相似度剪枝算法。

该算法首先基于改进的Jaccard相似度度量计算全图边集相似度矩阵,相似度计算公式为:

$$\mathrm{Sim}=\mathrm{min}\left(\frac{|N_u \cap N_v|+1}{|N_u|+1}, \frac{|N_u \cap N_v|+1}{|N_v|+1}\right)$$

其中 $N_u$ 和 $N_v$ 分别表示节点 $u$ 和节点 $v$ 的邻居节点集合。

随后,算法对每个节点实施度归一化剪枝策略——仅保留与其最相似的前K条邻接边,得到 自适应拓扑保持图 。这种自适应的局部剪枝机制在实现网络稀疏化的同时,有效保留了三种关键拓扑特征:

1. 社区内部高相似度核心连接;
2. 社区间桥接边;
3. 度分布异质性特征。

通过剪枝削弱了枢纽节点的过度连接,突出了社区内部紧密连接模式,使得社区结构更加清晰。同时,算法通过保留前 K 相似边的策略,在不同节点之间自适应地确定了剪枝阈值,既避免了采用全局阈值带来的"一刀切"问题,又充分考虑了度分布差异带来的非均匀影响。

为了评估 Top-K 相似度剪枝算法的效果,我们在包括 club 社交网络在内的 8 个基准数据集上进行了系统性的对照实验。通过设置不同的 K 值,比较剪枝前后的社区划分性能,我们发现当 K=5 时算法在社区检测任务中表现最佳。在该参数设置下,剪枝后的网络能够较好地保持原有的社区结构,并且显著提升了社区的模块度和聚类系数。

Top-K 相似度剪枝在简化网络拓扑的同时最大限度地保持了关键结构信息,是一种有效的预处理方法。通过嵌入到 Louvain 算法中,它能够显著提升社区检测的质量,为复杂网络的社区分析提供了新的思路。在后续的案例分析中,我们会进一步展示Top-K剪枝结合Louvain算法在实际网络中的应用效果。


[1] Blondel et al. Fast unfolding of communities in large networks, 2008.
[2] Lancichinetti et al. Limits of modularity maximization in community detection, 2011.
[3] Pons et al. Post-processing hierarchical community structures, 2016.
[4] Girvan & Newman. Community structure in social and biological networks, 2002.
[5] Traag et al. From Louvain to Leiden: guaranteeing well-connected communities, 2019.
[6] Rossetti et al. TILES: an online algorithm for community detection in dynamic social networks, 2017.
[7] Xu et al. Dynamic modularity optimization for scalable community detection, 2019.
[8] Bhatia et al. Dynamic community detection with graph neural networks, 2021.
[9] Kipf & Welling. Variational graph auto-encoders, 2016.
[10] Hamilton et al. Inductive representation learning on large graphs, 2017.
[11] Yang et al. A comparative study of community detection algorithms on real-world networks, 2022.
[12] Su et al. NEAT: Neighborhood embedding assisted community detection, 2020.


[1] Newman M E J, Girvan M. Finding and evaluating community structure in networks[J]. Physical review E, 2004.
[7] Cheng D, et al. GB-DBSCAN: A fast granular-ball based DBSCAN clustering algorithm[J]. Information Sciences, 2024.
[8] Li P Z, et al. EdMot: An Edge Enhancement Approach for Motif-aware Community Detection[C]. KDD, 2019.
[11] Xia S, et al. Granular ball computing classifiers for efficient, scalable and robust learning[J]. Information Sciences, 2019.







十号
方法首先写框架，一两句话写各个部分干了什么
基于相似度的网络简化
定义block
准备工作定义图、节点等，介绍louvain算法，定义新词
