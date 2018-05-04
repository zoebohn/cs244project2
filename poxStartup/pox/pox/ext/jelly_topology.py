import os
import sys
import networkx as nx
import json
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI, info
from mininet.log import setLogLevel
sys.path.append("../../")
from subprocess import Popen
from mininet.node import Controller, RemoteController, Node
from mininet.link import Link, Intf
#from time import sleep, time

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

    for node in graph.nodes():
        s = 's' + str(node)
        for neigh in graph.neighbors(node):
            if (node >= neigh):
                continue
            sn =  's' + str(neigh)
            net.addLink( s, sn, port1=neigh, port2=node)

def aggNet():

	CONTROLLER_IP='127.0.0.1'

	net = Mininet( topo=None,
               	build=False)

	net.addController( 'c0',
                  	controller=RemoteController,
                  	ip=CONTROLLER_IP,
                  	port=6633)

        graph_to_hosts_and_switches(net)

	net.start()
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	aggNet()