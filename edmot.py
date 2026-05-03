""" EdMot clustering class."""

import community
import networkx as nx
from tqdm import tqdm

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

class EdMot(object):
    """
    Edge Motif Clustering Class.
    """
    def __init__(self, graph, component_count, cutoff, SIM_Thread=0):
        """
        :param graph: NetworkX object.
        :param component_count: Number of extract motif hypergraph components.
        :param cutoff: Motif edge cut-off value.
        """
        self.graph = graph
        self.component_count = component_count
        self.cutoff = cutoff
        self.SIM_Thread = SIM_Thread

    def _overlap(self, node_1, node_2):
        """
        Calculating the neighbourhood overlap for a pair of nodes.
        :param node_1: Source node 1.
        :param node_2: Source node 2.
        :return neighbourhood overlap: Overlap score.
        """
        nodes_1 = self.graph.neighbors(node_1)
        nodes_2 = self.graph.neighbors(node_2)
        return len(set(nodes_1).intersection(set(nodes_2)))

    def _calculate_motifs(self):
        """
        Enumerating pairwise motif counts.
        """
        # print("\nCalculating overlaps.\n")
        edges = [e for e in self.graph.edges() if self._overlap(e[0], e[1]) >= self.cutoff]
        self.motif_graph = nx.from_edgelist(edges)

    def _extract_components(self):
        """
        Extracting connected components from motif graph.
        """
        # print("\nExtracting components.\n")
        components = [c for c in nx.connected_components(self.motif_graph)]
        components = [[len(c), c] for c in components]
        components.sort(key=lambda x: x[0], reverse=True)
        important_components = [components[comp][1] for comp
                                in range(self.component_count if len(components)>=self.component_count else len(components))]
        self.blocks = [list(graph) for graph in important_components]

    def _fill_blocks(self):
        """
        Filling the dense blocks of the adjacency matrix.
        """
        # print("Adding edge blocks.\n")
        new_edges = [(n_1, n_2) for nodes in self.blocks for n_1 in nodes for n_2 in nodes if n_1!= n_2]
        self.graph.add_edges_from(new_edges)

    def fit(self):
        """
        Clustering the target graph.
        """
        self._calculate_motifs()
        self._extract_components()
        self._fill_blocks()
        # partition = community.best_partition(self.graph)
        return self.graph
