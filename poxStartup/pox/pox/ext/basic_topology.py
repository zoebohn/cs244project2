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

def aggNet():

	CONTROLLER_IP='127.0.0.1'

	net = Mininet( topo=None,
               	build=False)

	net.addController( 'c0',
                  	controller=RemoteController,
                  	ip=CONTROLLER_IP,
                  	port=6633)

	h1 = net.addHost( 'h1', ip='10.1.2.1')
	h2 = net.addHost( 'h2', ip='10.1.3.1')
	h3 = net.addHost( 'h3', ip='10.3.2.1')
	h4 = net.addHost( 'h4', ip='10.3.3.1')
	#h1 = net.addHost( 'h1', ip='0.0.0.0' )
	#h2 = net.addHost( 'h2', ip='0.0.0.0' )
	#h3 = net.addHost( 'h3', ip='0.0.0.0' )
	#h4 = net.addHost( 'h4', ip='0.0.0.0' )
	s1 = net.addSwitch( 's1', ip='10.1.0.1')
	s2 = net.addSwitch( 's2', ip='10.2.0.1')
	s3 = net.addSwitch( 's3', ip='10.3.0.1')
        s4 = net.addSwitch( 's4', ip ='10.2.1.1')

        net.addLink( s1, s2 , port1=5, port2=6, addr1='0e:0e:0e:0e:0e:01', addr2='0e:0e:0e:0e:0e:02')
	net.addLink( s2, s3 )

        net.addLink( h2, s4 )
        net.addLink( h4, s4 )

	net.addLink( h1, s1 )
	net.addLink( h2, s1 )
	net.addLink( h3, s3 )
	net.addLink( h4, s3 )

	net.start()
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	aggNet()
