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
    ECMP = False#True
    ECMP_8 = False#True
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
        #ECMP 8
        if (ECMP):
            shortest_paths = [p for p in nx.all_shortest_paths(graph, node_i, node_j)]
            if (ECMP_8):
                shortest_paths = shortest_paths[:8]
            else:
                shortest_paths = shortest_paths[:64]
        else:
            shortest_paths = [p for p in nx.shortest_simple_paths(graph, node_i, node_j)]
            shortest_paths = shortest_paths[:8]
        
        for path in shortest_paths:
            i = 0
            while i + 1 < len(path):
                edge = (min(path[i], path[i + 1]), max(path[i], path[i + 1]))
                link_count[edge] += 1
                i += 1

    highest_count = max(link_count.items(), key=operator.itemgetter(1))[1]
    print highest_count
    rank_to_count = [0] * (highest_count + 1) 
    for key in link_count:
        count = link_count[key]
        for i in range(0, count + 1):
            print i
            print count + 1
            rank_to_count[i] += 1

    links_so_far = 0;
    for i in range(0, len(rank_to_count)):
        start_range = links_so_far
        end_range = rank_to_count[i] + links_so_far
        links_so_far += rank_to_count[i]
        print str(end_range) + "," str(i);
        

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
