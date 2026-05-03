EdMot
================================
[![Arxiv](https://img.shields.io/badge/ArXiv-1906.04560-orange.svg)](https://arxiv.org/abs/1906.04560) [![codebeat badge](https://codebeat.co/badges/70ecf9b1-226c-487a-bbc7-9e6eedbf7e22)](https://codebeat.co/projects/github-com-benedekrozemberczki-edmot-master) [![repo size](https://img.shields.io/github/repo-size/benedekrozemberczki/EdMot.svg)](https://github.com/benedekrozemberczki/EdMot/archive/master.zip) [![benedekrozemberczki](https://img.shields.io/twitter/follow/benrozemberczki?style=social&logo=twitter)](https://twitter.com/intent/follow?screen_name=benrozemberczki)

A **NetworkX** implementation of *"EdMot: An Edge Enhancement Approach for Motif-aware Community Detection"* (KDD 2019).
<p align="center">
  <img width="800" src="edmot.jpg">
</p>


---------------------------------

### Abstract
<p align="justify">
网络社区检测是网络分析领域的一个热门研究课题。虽然目前已经提出了很多社区检测方法，但大多数方法只考虑了单个节点和边层次上的低阶网络结构。因此，它们无法捕捉到小型密集子图模式（如图案）层面的高阶特征。最近，人们开发出了一些高阶方法，但这些方法通常侧重于基于图案的超图，并假定其为连通图。然而，在现实世界的某些网络中，这种假设无法得到保证。特别是，超图可能会变得支离破碎。也就是说，尽管原始网络是一个连通图，但它可能由大量的连通成分和孤立节点组成。因此，现有的高阶方法会受到上述碎片化问题的严重影响，因为在这些方法中，超图中没有连接的节点即使属于同一个社区，也不能被组合在一起。为了解决上述碎片化问题，我们提出了一种边缘增强方法（Edge enhancement approach for Motif-aware community detection，简称 EdMot）。其主要思路如下。首先，构建一个基于图案的超图，并将超图中前 K 个最大的连接成分划分为模块。然后，通过构建一个边集，从每个模块中导出一个小块，从而加强每个模块内部的连接结构。根据新的边集，增强输入网络的原始连通性结构，生成重新布线的网络，从而充分利用基于图案的高阶结构，并很好地解决超图碎片化问题。最后，对重新布线的网络进行分区，以获得高阶群落结构。我们在八个真实世界的数据集上进行了广泛的实验，结果表明所提出的方法在提高最先进方法的社群检测性能方面非常有效。

该模型现在也可以在 [Karate Club](https://github.com/benedekrozemberczki/karateclub) 软件包中找到。

该资源库提供了论文中描述的 EdMot 的 NetworkX 实现：


> EdMot: An Edge Enhancement Approach for Motif-aware Community Detection
> Pei-Zhen Li, Ling Huang, Chang-Dong Wang, and  Jian-Huang Lai .
> KDD, 2019.
> [[Paper]](https://arxiv.org/abs/1906.04560)

A Matlab implementation of EdMot is available [[here]](https://github.com/lipzh5/EdMot_pro).

### Requirements
The codebase is implemented in Python 3.5.2. package versions used for development are just below.
```
networkx          2.4
tqdm              4.28.1
pandas            0.23.4
texttable         1.5.0
argparse          1.1.0
python-louvain    0.11
```
### Datasets
代码以 csv 文件形式获取图形的边列表。每一行表示两个节点之间的一条边，中间用逗号隔开。第一行是标题。节点的索引应从 0 开始。`input/`目录中包含了`Cora`的示例图。


### Options
训练模型由 `src/main.py` 脚本处理，该脚本提供以下命令行参数。

#### Input and output options
```
  --edge-path         STR    Edge list csv.       Default is `input/cora_edges.csv`.
  --membership-path   STR    Features json.       Default is `output/cora_membership.json`.
```
#### Model options
```             
  --cutoff       INT     Random seed.                   Default is 2.
  --components   INT     Number of motif components.    Default is 1.
```
### Examples
以下命令可学习 EdMot 集群。
```sh
$ python src/main.py
```
<p align="center">
<img style="float: center;" src="edmot.gif">
</p>

Increasing the motif graph component number.
```sh
$ python src/main.py --components 2
```
--------------------------------------------------------------------------------

**License**

- [GNU License](https://github.com/benedekrozemberczki/EdMot/blob/master/LICENSE)

--------------------------------------------------------------------------------
