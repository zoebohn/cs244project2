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
            nodes = graph.nodes()
            
            count = 1
            for node in nodes: 
                nodeHost = self.addHost( 'h' + str(count))
                neighbors = graph.neighbors(node)
                ncount = 1;
                for neighbor in neighbors:
                    # todo don't add things twice
                    neighborHost = self.addHost( 'h' + str(count) + 'n' + str(ncount))
                    leftSwitch = self.addSwitch( 'sh' + str(count) + 'n' + str(ncount) + '1')
                    rightSwitch = self.addSwitch( 'sh' + str(count) + 'n' + str(ncount) + '2')
                    self.addLink(nodeHost, leftSwitch)
                    self.addLink(leftSwitch, rightSwitch)
                    self.addLink(rightSwitch, neighborHost)
                    ncount += 1
                count += 1
            
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

