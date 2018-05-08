import networkx as nx
import json
from sys import argv

def main():
    nodes = int(argv[1]) #6
    degree = int(argv[2]) #3
    graph = nx.random_regular_graph(degree, nodes)
    graph = graph.to_directed()
    data = nx.readwrite.node_link_data(graph)
    with open('generated_rrg', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    main()
