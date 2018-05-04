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

        h1 = net.addHost( 'h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
        h2 = net.addHost( 'h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
        h3 = net.addHost( 'h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
        h4 = net.addHost( 'h4', ip='10.0.0.4', mac='00:00:00:00:00:04')
	#h1 = net.addHost( 'h1', ip='0.0.0.0' )
	#h2 = net.addHost( 'h2', ip='0.0.0.0' )
	#h3 = net.addHost( 'h3', ip='0.0.0.0' )
	#h4 = net.addHost( 'h4', ip='0.0.0.0' )
        s1 = net.addSwitch( 's1', ip='10.1.0.0', mac='00:00:00:01:00:00')
        s2 = net.addSwitch( 's2', ip='10.2.0.0', mac='00:00:00:02:00:00')
        s3 = net.addSwitch( 's3', ip='10.3.0.0', mac='00:00:00:03:00:00')
        s4 = net.addSwitch( 's4', ip ='10.4.0.0', mac='00:00:00:04:00:00')

        net.addLink( s1, s2 , port1=1, port2=2)
	net.addLink( s2, s3 , port1=3, port2=4)

        net.addLink( s2, s4, port1=5, port2=6)
        net.addLink( s4, s3, port1=7, port2=8)

	net.addLink( h1, s1, port1=9, port2=10)
	net.addLink( h2, s1, port1=11, port2=12)
	net.addLink( h3, s3, port1=13, port2=14)
	net.addLink( h4, s3, port1=15, port2=16)

#       net.addLink( s1, s2 , port1=1, addr1='00:00:00:00:01:00', port2=2, addr2='00:00:00:00:02:00')
#	net.addLink( s2, s3 , port1=3, addr1='00:00:00:00:02:00', port2=4, addr2='00:00:00:00:03:00')

#        net.addLink( h2, s4, port1=5, addr1='00:00:00:00:00:02', port2=6, addr2='00:00:00:00:04:00')
#        net.addLink( h4, s4, port1=7, addr1='00:00:00:00:00:04', port2=8, addr2='00:00:00:00:04:00')

#	net.addLink( h1, s1, port1=9, addr1='00:00:00:00:00:01', port2=10, addr2='00:00:00:00:01:00')
#	net.addLink( h2, s1, port1=11, addr1='00:00:00:00:00:02', port2=12, addr2='00:00:00:00:01:00')
#	net.addLink( h3, s3, port1=13, addr1='00:00:00:00:00:03', port2=14, addr2='00:00:00:00:03:00')
#	net.addLink( h4, s3, port1=15, addr1='00:00:00:00:00:04', port2=16, addr2='00:00:00:00:03:00')

	net.start()
	CLI( net )
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	aggNet()
