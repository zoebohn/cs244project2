import networkx as nx
import json
import operator
from itertools import islice
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    data = None
    with open('figure9_rrg', 'r') as infile:
        data = json.load(infile)
    graph = nx.readwrite.node_link_graph(data)
    x, y = generate_data(graph, True, True)
    ecmp_plot = plt.step(x, y, label="8-way ECMP")
    x, y = generate_data(graph, True, False)
    ecmp64_plot = plt.step(x, y, label="64-way ECMP")
    x, y = generate_data(graph, False, False)
    kshortest_plot = plt.step(x, y, label="8 Shortest Paths")
    plt.legend()
    plt.xlabel("Rank of Link")
    plt.ylabel("# Distinct Paths Link is On")
    plt.xlim(xmin=0, xmax=3000)
    plt.ylim(ymin=0, ymax=25)
    plt.savefig('Figure9.png')

def bfs_paths(graph, start, goal):
    queue = [(start, [start])]
    limit = 0
    while queue and limit < 7:
        (vertex, path) = queue.pop(0)
	for next in set(graph.neighbors(vertex)) - set(path):
            if next == goal:
		limit += 1
		yield path + [next]
            else:
                queue.append((next, path + [next]))

def generate_data(graph, ecmp, ecmp_8):
    ECMP = ecmp
    ECMP_8 = ecmp_8
    link_count = {}
    for edge in graph.edges():
        link_count[edge] = 0

    for node_i in graph.nodes():
        node_j = node_i + 1
        if (node_j == len(graph.nodes())):
            node_j = 1
        #ECMP 8
        if (ECMP):
            if (ECMP_8):
                shortest_paths = list(islice(nx.all_shortest_paths(graph, node_i, node_j), 7))
            else:
                shortest_paths = list(islice(nx.all_shortest_paths(graph, node_i, node_j), 63))
        else:
            	shortest_paths = list(bfs_paths(graph, node_i, node_j))[:7]
		#shortest_paths = list(islice(nx.shortest_simple_paths(graph, node_i, node_j), 4))
        
        for path in shortest_paths:
            i = 0
            while (i + 1) < len(path):
                edge = (path[i], path[i + 1])
                link_count[edge] += 1
                i += 1

    
    highest_count = max(link_count.items(), key=operator.itemgetter(1))[1]
    rank_to_count = [0] * (highest_count + 1) 
    for key in link_count:
        count = link_count[key]
        for i in range(count, len(rank_to_count)):
            rank_to_count[i] += 1
    x = []
    y = []
    for i in range(0, len(rank_to_count)):
        end_range = rank_to_count[i]
        x.append(end_range)
        y.append(i)
    return x, y
