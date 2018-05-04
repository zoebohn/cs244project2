import networkx as nx
import json
from collections import defaultdict
from itertools import islice


def graph_to_dicts():
    def host_ip(node):
        return '10.0.0' + str(node)

    def switch_ip(node):
        return '10.' + str(node) + '.1.0'
    
    data = None
    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    graph = nx.readwrite.node_link_graph(data)
    
    ecmp_path_map = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:None)))
    link_to_port = defaultdict(lambda:defaultdict(lambda:None))
    ip_to_dpid = defaultdict(lambda:None)
    hosts = []

    host_to_ip = {}
    switch_to_ip = {}

    # set host and switch ips (every switch gets one host)
    for node in graph.nodes():
        switch_to_ip[node] = switch_ip(node) 
        host_to_ip[node] = host_ip(node) 
        hosts.append(host_to_ip[node])
    # dpids for switches 
        ip_to_dpid[switch_to_ip[node]] = node
    
    # links to ports
    for node in graph.nodes():
        host_ip = host_to_ip[node]
        switch_ip = switch_to_ip[node]
        link_to_port[host_ip][switch_ip] = node 
        link_to_port[switch_ip][host_ip] = node 
        for neigh in graph.neighbors(node):
            neigh_switch_ip = switch_to_ip[neigh]
            link_to_port[neigh_switch_ip][switch_ip] = node 
            link_to_port[switch_ip][neigh_switch_ip] = neigh 

    # set path ips
    for node_i in graph.nodes():
        node_j = node_i + 1
        if (node_j == len(graph.nodes())):
            node_j = 0
        ecmp_paths = list(islice(nx.all_shortest_paths(graph, node_i, node_j), 7))
        #k_paths = list(islice(nx.shortest_simple_paths(graph, node_i, node_j), 4))

        ecmp_ip_paths = []
        for ecmp_path in ecmp_paths:
            ecmp_ip_path = []
            print "ecmp_path" + str(ecmp_path)
            for i in range(0, len(ecmp_path)):
                ecmp_ip_path.append(switch_to_ip[ecmp_path[i]])
            # add end host
            ecmp_ip_path.append(host_to_ip[ecmp_path[len(ecmp_path) - 1]])
            ecmp_ip_paths.append(ecmp_ip_path)


        src_ip = host_to_ip[node_i]
        dst_ip = host_to_ip[node_j]
        print "source node: " + str(node_i)
        print "dst node: " + str(node_j)
        print "source ip: " + src_ip
        print "dst ip: " + dst_ip
        print "paths: " + str(ecmp_ip_paths)
        print ""

        ecmp_path_map[src_ip][dst_ip] = ecmp_ip_paths

    #print ecmp_path_map
    return hosts, ecmp_path_map, link_to_port, ip_to_dpid

'''
def graph_to_hosts_and_switches(net):
    def host_ip(node):
        return '10.0.0' + str(node)

    def switch_ip(node):
        return '10.' + str(node) + '.1.0'
    data = None
    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    graph = nx.readwrite.node_link_graph(data)
   
    for node in graph.nodes():
        h = net.addHost( 'h' + str(node), ip=host_ip(node))
        s = net.addSwitch( 's' + str(node), ip=switch_ip(node))
        net.addLink( h, s, port1=node, port2=node)
        for neigh in graph.neighbors(node):
            if (node >= neigh):
                continue # don't repeat edges
            sn = net.addSwitch( 's' + str(neigh), ip=switch_ip(neigh))
            net.addLink( s, sn, port1=neigh, port2=node)
    return 
'''
graph_to_dicts()
