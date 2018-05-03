import os
import sys
import networkx as nx
import json
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
sys.path.append("../../")
from pox.ext.jelly_pox import JELLYPOX
from subprocess import Popen
#from time import sleep, time

class JellyFishTop(Topo):
    ''' TODO, build your topology here'''
    def __init__(self):
            Topo.__init__(self)
            self.id_gen = JellyFishId
            #graph = nx.random_regular_graph(4, 10)   #(d, n, seed=None)
            #graph = graph.to_directed()
            with open('generated_rrg', 'r') as infile:
                data = json.load(infile)
            graph = nx.readwrite.node_link_graph(data)
            nodes = graph.nodes()
           
            # todo not repeating edges now, but don't double create hosts (?)
            nodeToHost = {}
            for node in nodes:
                hostString = 'h' + str(node)
                nodeHost = self.addHost(hostString)
                nodeToHost[node] = nodeHost

            for node in nodes: 
                nodeHost = nodeToHost[node]
                neighbors = graph.neighbors(node)
                print("node: " + str(node))
                for neighbor in neighbors:
                    print("neighbor: " + str(neighbor))
                    if (neighbor < node):
                        continue
                    neighborHost = nodeToHost[neighbor]
                    
                    leftString = 's' + str(node) + 'x' + str(neighbor)
                    rightString = 's' + str(neighbor) + 'x' + str(node)
                    leftSwitch = self.addSwitch(leftString)
                    rightSwitch = self.addSwitch(rightString)
                    
                    self.addLink(nodeHost, leftSwitch)
                    self.addLink(leftSwitch, rightSwitch)
                    self.addLink(rightSwitch, neighborHost)
                print("***")
            #leftHost = self.addHost( 'h1' )
            #rightHost = self.addHost( 'h2' )
            #leftSwitch = self.addSwitch( 's3' )
            #rightSwitch = self.addSwitch( 's4' )

            # Add links
            #self.addLink( leftHost, leftSwitch )
            #self.addLink( leftSwitch, rightSwitch )
            #self.addLink( rightSwitch, rightHost )


class NodeID(object):
    '''Topo node identifier.'''

    def __init__(self, dpid = None):
        '''Init.
        @param dpid dpid
        '''
        # DPID-compatible hashable identifier: opaque 64-bit unsigned int
        self.dpid = dpid

    def __str__(self):
        '''String conversion.
        @return str dpid as string
        '''
        return str(self.dpid)

    def name_str(self):
        '''Name conversion.
        @return name name as string
        '''
        return str(self.dpid)

    def ip_str(self):
        '''Name conversion.
        @return ip ip as string
        '''
        hi = (self.dpid & 0xff0000) >> 16
        mid = (self.dpid & 0xff00) >> 8
        lo = self.dpid & 0xff
        return "10.%i.%i.%i" % (hi, mid, lo)
 

class JellyFishId(NodeID):
    def __init__(self, pod = 0, sw = 0, host = 0, dpid = None, name = None):
        '''Create FatTreeNodeID object from custom params.
        Either (pod, sw, host) or dpid must be passed in.
        @param pod pod ID
        @param sw switch ID
        @param host host ID
        @param dpid optional dpid
        @param name optional name
        '''
        if dpid:
            self.sw = (dpid & 0xff00) >> 8
            self.host = (dpid & 0xff)
            self.dpid = dpid
        elif name:
            sw, host = [int(s) for s in name.split('_')]
            self.sw = sw
            self.host = host
            self.dpid = (sw << 8) + host
        else:
            self.host = host
            self.sw = sw
            self.dpid = (sw << 8) + host

    def __str__(self):
        return "(%i, %i)" % (self.host, self.sw)

    def name_str(self):
        '''Return name string'''
        return "%i_%i" % (self.host, self.sw)

"""
def experiment(net):
        net.start()
        sleep(3)
        net.pingAll()
        net.stop()

def main():
	topo = JellyFishTop()
	net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
        setLogLevel('info')
        experiment(net)
"""
topos = {'jellyfish': JellyFishTop}

#if __name__ == "__main__":
#	main()

