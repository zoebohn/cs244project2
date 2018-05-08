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
from mininet.link import TCLink, Intf
import re
from sys import argv
#from time import sleep, time

def graph_to_hosts_and_switches(net):
    def host_ip(node):
        return '10.0.0' + str(node)
    def switch_ip(node):
        return '10.' + str(node) + '.0.0'
    def host_mac(node):
        return '00:00:00:00:00:' + str(node)
    def switch_mac(node):
        return '00:00:00:' + str(node) + ':00:00'
    data = None
    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    graph = nx.readwrite.node_link_graph(data)

    for node_orig in graph.nodes():
        node = node_orig + 1
        h = net.addHost( 'h' + str(node), ip=host_ip(node), mac=host_mac(node))
        print "mac is " + switch_mac(node) + ', ' + host_mac(node)
        s = net.addSwitch( 's' + str(node), ip=switch_ip(node), mac=switch_mac(node))
        net.addLink( h, s, bw=10, port1=node, port2=node)

    for node_orig in graph.nodes():
        node = node_orig + 1
        s = 's' + str(node)
        for neigh_orig in graph.neighbors(node_orig):
            neigh = neigh_orig + 1
            if (node >= neigh):
                continue
            sn =  's' + str(neigh)
            net.addLink( s, sn, bw=10, port1=neigh, port2=node)

def runThroughputTest(net, numFlows, runNum, ecmp):
    info( '*** Starting run %s ***' % runNum)
    for dest in net.hosts:
        dest.cmd( "iperf -s &" )
        info('starting %s\n' % dest.name)
    prev = net.hosts[len(net.hosts) - 1]
    i = 0
    while i < len(net.hosts):
        curr = net.hosts[i]
        info('conn between %s and %s' % (prev.name, curr.name))
        prev.sendCmd("iperf -t %s -P %s -i %s -f k -i .5 -c %s > tests/test_host%s_run%s_flows%s_ecmp%s" % (5, numFlows, 5, curr.IP(), i, runNum, numFlows, ecmp ) )
        prev = curr
        i += 1
    info ('*** Running iperf ***')
    results = []
    prev = net.hosts[len(net.hosts) - 1]
    i = 0
    while i < len(net.hosts):
        curr = net.hosts[i]
        result = prev.waitOutput()
        #curr.cmd("kill -9 %iperf")
        #curr.cmd("wait")
        info("output: %s" % result)
        prev = curr
        i += 1

def aggNet():

	CONTROLLER_IP='127.0.0.1'

        ecmp = argv[1] == "ecmp"
        numRuns = 5
        
        # run with 1 flow

        for i in range(0, numRuns):

	    net = Mininet( topo=None,
               	build=False, link=TCLink)

	    net.addController( 'c0',
                  	controller=RemoteController,
                  	ip=CONTROLLER_IP,
                  	port=6633)

            graph_to_hosts_and_switches(net)

	    net.start()
	    runThroughputTest(net, 1, i, ecmp)
            #CLI( net )
	    net.stop()

        # run with 8 flows
        
        for i in range(0, numRuns):

	    net = Mininet( topo=None,
               	build=False, link=TCLink)

	    net.addController( 'c0',
                  	controller=RemoteController,
                  	ip=CONTROLLER_IP,
                  	port=6633)

            graph_to_hosts_and_switches(net)

	    net.start()
	    runThroughputTest(net, 8, i, ecmp)
            #CLI( net )
	    net.stop()


if __name__ == '__main__':
	setLogLevel( 'info' )
	aggNet()
