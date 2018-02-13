import graph_tool.all as gt


def parse_input(graph_file):
    color_target = 0
    graph = gt.Graph()
    graph.set_directed(is_directed=False)

    with open(graph_file, 'r') as in_file:
        lines = in_file.readlines()
        color_target = int(lines[0])
        for i in range(1, len(lines)):
            source = lines[i].split(' ')[0]
            target = lines[i].split(' ')[1]
            graph.add_edge(source=int(source), target=int(target))
            # print("added edge " + source + ' ' + target)
            # print(i)
            if int(source) == int(target):
                print("self edge")

    return color_target, graph


c, g = parse_input("jean.g")

# pos = gt.arf_layout(g)
gt.graph_draw(g) # , pos=pos)

for edge in g.edges():
    print(edge)