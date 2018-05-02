import networkx as nx
import json
import operator

def main():
    data = None
    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    graph = nx.readwrite.node_link_graph(data)
    ECMP(graph)

def ECMP(graph):
    source = 0
    target = 8
    link_count = {}
    for node_i in graph.nodes():
        for node_j in graph.nodes():
            if node_i >= node_j:
                continue
            edge = (node_i, node_j)
            link_count[edge] = 0

    for node_i in graph.nodes():
        node_j = node_i + 1
        if (node_j == len(graph.nodes())):
            node_j = 1
        shortest_paths = [p for p in nx.all_shortest_paths(graph, node_i, node_j)]
        #ECMP 8
        shortest_paths = shortest_paths[:8]
        for path in shortest_paths:
            i = 0
            while i + 1 < len(path):
                edge = (min(path[i], path[i + 1]), max(path[i], path[i + 1]))
                link_count[edge] += 1
                i += 1
    for key in link_count: 
        print "Edge: " + str(key[0]) + "-" + str(key[1]) + ". Appears on " + str(link_count[key]) + " paths."

"""
def YenKSP(graph, source, target, K):
    l, shortest_path = nx.single_source_dijkstra(graph, source, target)
    A = []
    A.append(shortest_path)

    B = []

    for k in range(1, K):
        for i in range(0, size(A[k - 1]) - 1):
            spurNode = A[k-1][i]
            rootPath = A[k-1][:i]

            removed_edges = []; removed_root_edges = []; removed_root_nodes = [];

            for path in A:
                if rootPath == p[:i]

"""

if __name__ == "__main__":
    main()
