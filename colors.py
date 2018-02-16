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
        self.mutation_rate = 0.01

    def initialize(self, graph_size, color_limit):
        for i in range(graph_size):
            self.coloring[i] = 0  # TODO: pick a color at random from 0 to color limit

    def mutate(self):
        for i in range(len(self.coloring)):
            # TODO: make this happen a if rand [0,1] is < mutation_rate
            self.coloring[i] = 0  # TODO: pick a new random color from 0 to color limit

    def crossover(self, other):
        # other is an individual - single point crossover
        # TODO: pick a number at random between 0 and size of graph - replace the 0 with that number
        for i in range(0, len(self.coloring)):
            self.coloring[i] = other.coloring[i]


class Population:
    def __init__(self):
        self.pop_size = 0
        self.pop = []

    def initialize(self, pop_size, graph_size, color_limit):
        self.pop_size = pop_size
        self.pop = [Individual().initialize(graph_size=graph_size, color_limit=color_limit) for _ in range(pop_size)]

    def select(self):
        # pick 2 things at random, hold a tournament, and the winner survives. Repeat until new pop is full
        index_one = 0
        index_two = 1
        if self.pop[index_one].fitness() > self.pop[index_two].fitness():
            return self.pop[index_one]
        else:
            return self.pop[index_two]

    def mutate(self):
        pass


class Experiment:
    def __init__(self):
        self.input_filename = ""
        self.pop = Population()
        self.color_limit = 0
        self.graph = 0
        self.pop_size = 100
        self.generations = 1000

    def initialize(self, input_filename):
        self.input_filename = input_filename
        self.color_limit, self.graph = parse_input(self.input_filename)
        self.pop.initialize(pop_size=self.pop_size, graph_size=self.graph.size(), color_limit=self.color_limit)
        # TODO: check graph size syntax

    def fitness(self, individual):
        total = 0
        number_of_edges = 0
        for edge in self.graph.edges():
            if individual.coloring[edge[0]] != individual.coloring[edge[1]]:
                total += 1

        return total / number_of_edges

    def run_generation(self):
        # evaluate, select (& crossover), mutate
        for i in range(self.pop.pop_size):
            pass  # TODO: for edge in graph, check if that element's edge is satisfied. Div by # of edges.


# ideas to improve things:
# make crossover apply to a min-cut of the graph, instead of just at random location
# make mutation expect 1 per individual per invocation
# have selection use elitism to keep fittest individual in the population

