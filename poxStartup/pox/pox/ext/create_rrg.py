import networkx as nx
import json

def main():
    graph = nx.random_regular_graph(6, 686)
    graph = graph.to_directed()
    data = nx.readwrite.node_link_data(graph)
    with open('generated_rrg', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    main()
