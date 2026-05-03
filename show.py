import collections
import webbrowser

from pyecharts import options as opts
from pyecharts.charts import Graph


def show_core(G, communities):
    """
    可视化挖掘出的核心社区
    :param G:
    :param communities:
    :return:
    """
    # 创建颜色映射字典
    color_mapping = {
        0: "#e6194b", 1: "#3cb44b", 2: "#ffe119", 3: "#4363d8", 4: "#f58231",
        5: "#911eb4", 6: "#46f0f0", 7: "#f032e6", 8: "#bcf60c", 9: "#fabebe",
        10: "#008080", 11: "#e6beff", 12: "#9a6324", 13: "#fffac8", 14: "#800000",
        15: "#aaffc3", 16: "#808000", 17: "#ffd8b1", 18: "#000075"
        # 如果你的社区数量超过20个，你需要在这里添加更多颜色
    }
    nodes = []
    # 遍历所有节点并初始化颜色
    for node in G.nodes():
        # 默认颜色和样式
        node_data = {"name": str(node), "symbolSize": 50, "itemStyle": {"color": "gray"}}

        # 检查节点属于哪个社区，修改颜色为对应的社区颜色
        for i, community in enumerate(communities):
            if node in community:
                node_data["itemStyle"]["color"] = color_mapping[i]
                break  # 节点最多属于一个社区，找到后可以直接退出
        # 添加节点到列表
        nodes.append(node_data)

    edges = []
    for source, target in G.edges():
        edges.append({"source": str(source), "target": str(target)})

    # 绘制图表
    graph = (
        Graph(init_opts=opts.InitOpts(width="3000px", height="1500px"))
        .add(
            "",
            nodes,
            edges,
            repulsion=4000,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),  # 在节点底部显示编号
            edge_label=opts.LabelOpts(
                is_show=False,
                formatter="{c}",
                position="middle",
            ),  # 在边的中间显示边的权重
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="graph", pos_left='center'),
            graphic_opts=opts.GraphicGroup(
                graphic_item=opts.GraphicItem(left="center", top="center"))
        )
    )
    graph.render('graph.html')
    # 打开浏览器并显示图表
    webbrowser.open('graph.html')


def show_unsigned_nodes(G, communities, unsigned_nodes):
    """
    可视化社区和一些未被划分的节点
    :param G:
    :param communities:
    :param unsigned_nodes:
    :return:
    """
    # 创建颜色映射字典
    color_mapping = {
        0: "#e6194b", 1: "#3cb44b", 2: "#ffe119", 3: "#4363d8", 4: "#f58231",
        5: "#911eb4", 6: "#46f0f0", 7: "#f032e6", 8: "#bcf60c", 9: "#fabebe",
        10: "#008080", 11: "#e6beff", 12: "#9a6324", 13: "#fffac8", 14: "#800000",
        15: "#aaffc3", 16: "#808000", 17: "#ffd8b1", 18: "#000075"
        # 如果你的社区数量超过20个，你需要在这里添加更多颜色
    }
    nodes = []
    # 遍历所有节点并初始化颜色
    for node in G.nodes():
        # 默认颜色和样式
        node_data = {"name": str(node), "symbolSize": 50, "itemStyle": {"color": "lightblue"}}

        # 如果节点在 unsigned_nodes 中，修改为灰色
        if node in unsigned_nodes:
            node_data["itemStyle"]["color"] = "gray"

        # 检查节点属于哪个社区，修改颜色为对应的社区颜色
        for i, community in enumerate(communities):
            if node in community:
                node_data["itemStyle"]["color"] = color_mapping[i]
                break  # 节点最多属于一个社区，找到后可以直接退出
        # 添加节点到列表
        nodes.append(node_data)

    edges = []
    for source, target in G.edges():
        edges.append({"source": str(source), "target": str(target)})

    # 绘制图表
    graph = (
        Graph(init_opts=opts.InitOpts(width="3000px", height="1500px"))
        .add(
            "",
            nodes,
            edges,
            repulsion=4000,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),  # 在节点底部显示编号
            edge_label=opts.LabelOpts(
                is_show=False,
                formatter="{c}",
                position="middle",
            ),  # 在边的中间显示边的权重
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="graph", pos_left='center'),
            graphic_opts=opts.GraphicGroup(
                graphic_item=opts.GraphicItem(left="center", top="center"))
        )
    )
    graph.render('graph.html')
    # 打开浏览器并显示图表
    webbrowser.open('graph.html')


# Show communities with pyecharts
def show_communities(name, G, communities):

    """
    可视化社区划分
    :param un:
    :param name: 数据名称
    :param G: 图对象G
    :param communities: 社区划分
    :return:
    """
    graph_name = name

    # 创建颜色映射字典
    color_mapping = {
        0: "#e6194b", 1: "#3cb44b", 2: "#ffe119", 3: "#4363d8", 4: "#f58231",
        5: "#911eb4", 6: "#46f0f0", 7: "#f032e6", 8: "#bcf60c", 9: "#fabebe",
        10: "#008080", 11: "#e6beff", 12: "#9a6324", 13: "#fffac8", 14: "#800000",
        15: "#aaffc3", 16: "#808000", 17: "#ffd8b1", 18: "#000075"
        # 如果你的社区数量超过20个，你需要在这里添加更多颜色
    }

    # 提取节点和边信息
    nodes = []
    num_colors = len(color_mapping)  # 获取颜色的数量

    # 构造节点列表，每个节点为一个字典
    for i, community in enumerate(communities):
        # 如果社区数量超过颜色的数量，循环使用颜色
        color_index = i % num_colors
        for node in community:
            nodes.append({"name": str(node), "symbolSize": 50, "itemStyle": {"color": color_mapping[color_index]}})

    edges = []
    for source, target in G.edges():
        edges.append({"source": str(source), "target": str(target)})

    # 绘制图表
    graph = (
        Graph(init_opts=opts.InitOpts(width="3000px", height="1500px"))
        .add(
            "",
            nodes,
            edges,
            repulsion=4000,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),  # 在节点底部显示编号
            edge_label=opts.LabelOpts(
                is_show=False,
                formatter="{c}",
                position="middle",
            ),  # 在边的中间显示边的权重
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=graph_name, pos_left='center'),
            graphic_opts=opts.GraphicGroup(
                graphic_item=opts.GraphicItem(left="center", top="center"))
        )
    )
    # 保存图表
    fixed_directory = "../community visualization/partition"
    file_path = f"{fixed_directory}/{graph_name}.html"
    graph.render(file_path)


def mix_colors(color1, color2, ratio=0.5):
    """
    Mixes two colors by averaging their RGB components.
    :param color1: The first color in hex format.
    :param color2: The second color in hex format.
    :param ratio: The ratio of mixing. Default is 0.5 (equal mix).
    :return: A hex string of the mixed color.
    """

    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

    def rgb_to_hex(rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    mixed_rgb = tuple(int(r1 * ratio + r2 * (1 - ratio)) for r1, r2 in zip(rgb1, rgb2))
    return rgb_to_hex(mixed_rgb)


def show_overlap_communities(name, G, communities):
    """
    :param name: 数据名称
    :param G: 图对象G
    :param communities: 社区划分
    :return:
    """
    graph_name = name

    # 创建颜色映射字典
    color_mapping = {
        0: "#e6194b", 1: "#3cb44b", 2: "#ffe119", 3: "#4363d8", 4: "#f58231",
        5: "#911eb4", 6: "#46f0f0", 7: "#f032e6", 8: "#bcf60c", 9: "#fabebe",
        10: "#008080", 11: "#e6beff", 12: "#9a6324", 13: "#fffac8", 14: "#800000",
        15: "#aaffc3", 16: "#808000", 17: "#ffd8b1", 18: "#000075", 19: "#808080"
        # 如果你的社区数量超过20个，你需要在这里添加更多颜色
    }

    # 提取节点和边信息
    nodes = []
    node_communities = {}

    # Build a mapping from node to the list of communities it belongs to
    for i, community in enumerate(communities):
        for node in community:
            if node not in node_communities:
                node_communities[node] = []
            node_communities[node].append(i)

    # Construct nodes with mixed colors for overlapping community membership
    for node, community_indices in node_communities.items():
        # Get the colors of all communities the node belongs to
        node_colors = [color_mapping[i] for i in community_indices]

        # If the node belongs to multiple communities, mix the colors
        if len(node_colors) > 1:
            mixed_color = node_colors[0]
            for color in node_colors[1:]:
                mixed_color = mix_colors(mixed_color, color)
        else:
            mixed_color = node_colors[0]

        # Determine the shape based on how many communities the node belongs to
        if len(community_indices) == 1:
            shape = "circle"  # Single community node
        elif len(community_indices) == 2:
            shape = "rect"  # Two community node (square)
        elif len(community_indices) == 3:
            shape = "triangle"  # Three community node (triangle)
        else:
            shape = "diamond"  # More than three, use diamond shape

        # Add node to the list with mixed color and shape
        nodes.append({
            "name": str(node),
            "symbolSize": 50,
            "symbol": shape,
            "itemStyle": {"color": mixed_color}
        })

    edges = []
    for source, target in G.edges():
        edges.append({"source": str(source), "target": str(target)})

    # 绘制图表
    graph = (
        Graph(init_opts=opts.InitOpts(width="3000px", height="1500px"))
        .add(
            "",
            nodes,
            edges,
            repulsion=4000,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),  # 在节点底部显示编号
            edge_label=opts.LabelOpts(
                is_show=False,
                formatter="{c}",
                position="middle",
            ),  # 在边的中间显示边的权重
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=graph_name, pos_left='center'),
            graphic_opts=opts.GraphicGroup(
                graphic_item=opts.GraphicItem(left="center", top="center"))
        )
    )
    # 保存图表
    fixed_directory = "../community visualization/overlaping_partition"
    file_path = f"{fixed_directory}/{graph_name}.html"
    graph.render(file_path)
