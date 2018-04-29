import os
import sys
import networkx as nx
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
sys.path.append("../../")
from pox.ext.jelly_pox import JELLYPOX
from subprocess import Popen
from time import sleep, time

class JellyFishTop(Topo):
    ''' TODO, build your topology here'''
    def build(self):
            graph = nx.random_regular_graph(2, 10)   #(d, n, seed=None)
            graph = graph.to_directed()
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
                    if (neighbor < node):
                        continue
                    print("neighbor: " + str(neighbor))
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

def experiment(net):
        net.start()
        sleep(3)
        net.pingAll()
        net.stop()

def main():
	topo = JellyFishTop()
	net = Mininet(topo=topo, host=CPULimitedHost, link = TCLink, controller=JELLYPOX)
	experiment(net)

if __name__ == "__main__":
	main()

