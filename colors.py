import graph_tool.all as gt
import random
from numpy.random import choice
import time
import math
import copy
import matplotlib.pyplot as plt


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


class Individual:
    def __init__(self):
        self.coloring = {}
        self.color_limit = 0
        self.graph_size = 0
        self.fitness = 0
        self.balanced_fitness = 0
        self.number_of_mutations = 1
        self.changed = True

    def initialize(self, graph_size, color_limit):
        self.graph_size = graph_size
        self.color_limit = color_limit
        self.number_of_mutations = math.ceil(self.graph_size / 20.0)
        for i in range(graph_size):
            self.coloring[i] = random.randint(0, color_limit - 1)

    def mutate(self):
        # pick n=number_of_mutations nodes at random without replacement
        choices = choice(self.graph_size, self.number_of_mutations, replace=False)
        for a in choices:
            self.coloring[a] = random.randint(0, self.color_limit - 1)
        self.changed = True

    def crossover(self, other):
        # other is an individual - single point crossover
        crossover_point = random.randint(0, self.graph_size - 1)
        for i in range(crossover_point, self.graph_size):
            self.coloring[i] = other.coloring[i]
        self.changed = True


class Population:
    def __init__(self):
        self.pop_size = 0
        self.graph_size = 0
        self.color_limit = 0
        self.edge_count = 0
        self.pop = []
        self.individuals_to_mutate = 10
        self.crossover_percent = 10
        self.fitness_array = []
        self.balanced_fitness_array = []

    def initialize(self, pop_size, graph_size, color_limit, edge_count, crossover_percent):
        self.pop_size = pop_size
        self.individuals_to_mutate = math.ceil(pop_size / 10.0)  # set this to 10% of the population
        self.graph_size = graph_size
        self.color_limit = color_limit
        self.edge_count = edge_count
        self.crossover_percent = crossover_percent
        self.pop = [Individual() for _ in range(pop_size)]
        self.fitness_array = [0 for _ in range(pop_size)]
        self.balanced_fitness_array = [0 for _ in range(pop_size)]
        for p in self.pop:
            p.initialize(graph_size=graph_size, color_limit=color_limit)

    def select(self):
        # pick 2 things at random, hold a tournament, and the winner is selected.
        choices = choice(self.pop, self.pop_size, replace=False)
        individual_one = choices[0]
        individual_two = choices[1]
        if individual_one.fitness > individual_two.fitness:
            return copy.deepcopy(individual_one)
        else:
            return copy.deepcopy(individual_two)

    def evaluate_fitness(self, graph):
        for i, individual in enumerate(self.pop):
            if individual.changed:
                total = 0
                for edge in graph.edges():
                    if individual.coloring[edge.source()] != individual.coloring[edge.target()]:
                        total += 1
                individual.fitness = total / self.edge_count
                self.fitness_array[i] = total / self.edge_count
                individual.changed = False

    def evaluate_balanced_fitness(self, graph):
        for i, individual in enumerate(self.pop):
            if individual.changed:
                total = 0
                for edge in graph.edges():
                    if individual.coloring[edge.source()] != individual.coloring[edge.target()]:
                        total += 1

                # initialize coloring
                coloration = [0 for _ in range(self.color_limit)]
                # count colors
                for _ in range(self.graph_size):
                    coloration[individual.coloring[_]] += 1
                # normalize coloration vector
                for _ in range(self.color_limit):
                    coloration[_] /= self.graph_size
                # calculate the product of the marginal coloration
                product = 1
                for _ in range(self.color_limit):
                    product *= coloration[_]

                # write out calculated values
                individual.fitness = total / self.edge_count
                self.fitness_array[i] = individual.fitness

                individual.balanced_fitness = individual.fitness * product / ((1.0/self.color_limit)**self.color_limit)
                self.balanced_fitness_array[i] = individual.balanced_fitness

                individual.changed = False

    def mutate(self):
        to_mutate = choice(self.pop_size, self.individuals_to_mutate, replace=False)
        for individual in to_mutate:
            self.pop[individual].mutate()

    def update_population(self):  # implements crossover
        new_pop = []
        current_size = 0
        # elitism - copy best individual
        new_pop.append(copy.deepcopy(self.pop[self.fitness_array.index(max(self.fitness_array))]))
        current_size += 1

        while current_size < self.pop_size:
            cross = random.randint(0, 99)
            # with prob = crossover_percent, choose two individuals by tournament select & cross them over then add
            if cross < self.crossover_percent:
                a = self.select()
                b = self.select()
                a.crossover(b)
                a.changed = True
                new_pop.append(a)
                current_size += 1
            # with prob = 1 - crossover_percent, choose an individual by tournament select & add
            else:
                new_pop.append(self.select())
                current_size += 1
        self.pop = new_pop


class Experiment:
    def __init__(self):
        self.input_filename = ""
        self.pop = Population()
        self.color_limit = 0
        self.graph = gt.Graph()
        self.pop_size = 100
        self.generations = 1000
        self.crossover_percent = 10
        self.progress = []

    def initialize(self, input_filename, pop_size, generations, crossover_percent):
        self.input_filename = input_filename
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_percent = crossover_percent
        self.color_limit, self.graph = parse_input(self.input_filename)
        self.pop.initialize(pop_size=self.pop_size, graph_size=self.graph.num_vertices(), color_limit=self.color_limit,
                            edge_count=self.graph.num_edges(), crossover_percent=self.crossover_percent)

    def run_generation(self):
        # evaluate, select (& crossover), mutate
        self.pop.evaluate_fitness(graph=self.graph)
        self.track_progress()
        self.pop.mutate()
        self.pop.update_population()
        pass

    def track_progress(self):
        maximum = max(self.pop.fitness_array)
        minimum = min(self.pop.fitness_array)
        avg = sum(self.pop.fitness_array) / self.pop_size
        self.progress.append([maximum, minimum, avg])

    def gen_graph(self):
        filename = 'results/' + self.input_filename + "_size" + str(self.pop_size) + "_generations" + str(self.generations)
        plt.plot(self.progress)
        plt.ylabel('fitness')
        plt.xlabel('generations')
        plt.show()
        # TODO: save plot of max, min, avg as pdf for easy import into latex

    def run_experiment(self):
        gens = 0
        while gens < self.generations:
            self.run_generation()
            gens += 1
        self.gen_graph()


start = time.time()
e = Experiment()
e.initialize(input_filename='queen5_5.g', pop_size=100, generations=300, crossover_percent=10)
e.run_experiment()
print(time.time() - start)
# print(e.pop.fitness_array)
# print(e.progress)
# print(e.pop.balanced_fitness_array)

# ideas to improve things:
# make crossover apply to a min-cut of the graph, instead of just at random location
# make mutation expect 1 per individual per invocation
# have selection use elitism to keep fittest individual in the population
