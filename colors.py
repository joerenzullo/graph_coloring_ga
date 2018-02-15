import graph_tool.all as gt


def parse_input(graph_file):
    graph = gt.Graph()
    graph.set_directed(is_directed=False)

    with open(graph_file, 'r') as in_file:
        lines = in_file.readlines()
        color_target = int(lines[0])
        for line in lines[1:]:
            source = int(line.split(' ')[0])
            target = int(line.split(' ')[1])
            if source < target:
                graph.add_edge(source=source, target=target, add_missing=True)
            else:
                graph.add_edge(source=target, target=source, add_missing=True)
            if source == target:
                print('error: tried to add loop')
            # print("added edge " + source + ' ' + target)
            # print(i)
            if int(source) == int(target):
                print("self edge")
    gt.remove_parallel_edges(graph)
    list_to_remove = []
    for vertex in graph.vertices():
        if graph.vertex(i=vertex).out_degree() == 0:
            list_to_remove.append(vertex)
    graph.remove_vertex(list_to_remove)

    return color_target, graph


c, g = parse_input("jean.g")

# pos = gt.arf_layout(g)
#
# for edge in g.edges():
#     print(edge)

# vertex_list = []
# for vertex in g.vertices():
#     vertex_list.append(vertex)
#
# print(g.get_out_degrees(vertex_list))

gt.graph_draw(g)  # , pos=pos)


class Individual:
    def __init__(self):
        self.coloring = {}
        self.fitness = 0

    def mutate(self):
        pass

    def crossover(self, other):
        # other is an individual
        pass


class Population:
    def __init__(self):
        self.pop = []

    def select(self):
        pass

    def mutate(self):
        pass


class Experiment:
    def __init__(self):
        self.input_graph = ""