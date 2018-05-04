from pox.core import core
from collections import defaultdict
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
import networkx as nx
import json
from itertools import islice

log = core.getLogger()

# [src][dst][curr-sw] -> port 
path_map = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:None)))

# [ip addr] -> mac addr
arp_table = defaultdict(lambda:None)

class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    self.dpid = connection.dpid

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """
    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.
    # Learn the port for the source MAC
    log.debug("packet is %s", packet)
    ipp = packet.find('ipv4')
    a = packet.find('arp')
    if ipp is not None:
        log.debug("Got packet from %s to %s at switch %d", ipp.srcip, ipp.dstip, self.dpid)
        log.debug("port to send to: %d", path_map[str(ipp.srcip)][str(ipp.dstip)][self.dpid][0])
        self.resend_packet(packet_in, path_map[str(ipp.srcip)][str(ipp.dstip)][self.dpid][0])
    elif a is not None:
        if packet.payload.opcode == arp.REQUEST:
            log.debug("protodst is %s", a.protodst)
            '''
            arp_reply = arp()
            arp_reply.hwtype = a.hwtype
            arp_reply.prototype = a.prototype
            arp_reply.hwlen = a.hwlen
            arp_reply.protolen = a.protolen
            arp_reply.opcode = arp.REPLY
            arp_reply.hwdst = a.hwsrc
            arp_reply.protodst = a.protosrc
            arp_reply.protosrc = a.protodst
            arp_reply.hwsrc = arp_table[a.protodst]
            e = ethernet()
            e.type = ethernet.ARP_TYPE
            e.dst = packet.src
            e.src = arp_table[a.protodst]
            e.payload = arp_reply
            self.resend_packet(e.pack(), of.OFPP_IN_PORT)
            '''
    else:
        log.warning("ERROR: packet is not IP. Dropping")

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    print "**got packet at switch " + str(event.dpid) + "***"
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    #print "Src: " + str(packet.src)
    #print "Dest: " + str(packet.dst)
    #print "Event port: " + str(event.port)
    #log.info("packet in")
    self.act_like_switch(packet, packet_in)

def write_paths_wrapper():
  hosts = ['10.0.0.1','10.0.0.2','10.0.0.3','10.0.0.4']
  paths = defaultdict(lambda:defaultdict(lambda:[]))
  link_to_port = defaultdict(lambda:defaultdict(lambda:None))
  ip_to_dpid = defaultdict(lambda:None)

  # src dst - [[path 1] [path2]]; path 1: [first hop....dst]
  paths['10.0.0.1']['10.0.0.2'] = [['10.1.0.0', '10.0.0.2']]
  paths['10.0.0.1']['10.0.0.3'] = [['10.1.0.0', '10.2.0.0', '10.3.0.0', '10.0.0.3']]
  paths['10.0.0.1']['10.0.0.4'] = [['10.1.0.0', '10.2.0.0', '10.3.0.0', '10.0.0.4']]
  
  paths['10.0.0.2']['10.0.0.1'] = [['10.1.0.0', '10.0.0.1']]
  paths['10.0.0.2']['10.0.0.3'] = [['10.1.0.0', '10.2.0.0', '10.3.0.0', '10.0.0.3']]
  paths['10.0.0.2']['10.0.0.4'] = [['10.1.0.0', '10.2.0.0', '10.3.0.0', '10.0.0.4']]
  
  paths['10.0.0.3']['10.0.0.1'] = [['10.3.0.0', '10.2.0.0', '10.1.0.0', '10.0.0.1']]
  paths['10.0.0.3']['10.0.0.2'] = [['10.3.0.0', '10.2.0.0', '10.1.0.0', '10.0.0.2']]
  paths['10.0.0.3']['10.0.0.4'] = [['10.3.0.0', '10.0.0.4']]
  
  paths['10.0.0.4']['10.0.0.1'] = [['10.3.0.0', '10.2.0.0', '10.1.0.0', '10.0.0.1']]
  paths['10.0.0.4']['10.0.0.2'] = [['10.3.0.0', '10.2.0.0', '10.1.0.0', '10.0.0.2']]
  paths['10.0.0.4']['10.0.0.3'] = [['10.3.0.0', '10.0.0.3']]

  link_to_port['10.1.0.0']['10.2.0.0'] = 1
  link_to_port['10.2.0.0']['10.1.0.0'] = 2
  link_to_port['10.2.0.0']['10.3.0.0'] = 3
  link_to_port['10.3.0.0']['10.2.0.0'] = 4
  link_to_port['10.0.0.1']['10.1.0.0'] = 9
  link_to_port['10.1.0.0']['10.0.0.1'] = 10
  link_to_port['10.0.0.2']['10.1.0.0'] = 11
  link_to_port['10.1.0.0']['10.0.0.2'] = 12
  link_to_port['10.0.0.3']['10.3.0.0'] = 13
  link_to_port['10.3.0.0']['10.0.0.3'] = 14
  link_to_port['10.0.0.4']['10.3.0.0'] = 15
  link_to_port['10.3.0.0']['10.0.0.4'] = 16

  ip_to_dpid['10.1.0.0'] = 1
  ip_to_dpid['10.2.0.0'] = 2
  ip_to_dpid['10.3.0.0'] = 3
  ip_to_dpid['10.4.0.0'] = 4

  write_paths(hosts, paths, link_to_port, ip_to_dpid)

def jellyfish_graph_to_dicts():
    def host_ip(node):
        return '10.0.0.' + str(node)

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
    for node_orig in graph.nodes():
        node = node_orig + 1
        switch_to_ip[node] = switch_ip(node) 
        host_to_ip[node] = host_ip(node) 
        hosts.append(host_to_ip[node])
    # dpids for switches 
        ip_to_dpid[switch_to_ip[node]] = node
    
    # links to ports
    for node_orig in graph.nodes():
        node = node_orig + 1
        host_ip = host_to_ip[node]
        switch_ip = switch_to_ip[node]
        link_to_port[host_ip][switch_ip] = node 
        link_to_port[switch_ip][host_ip] = node 
        for neigh_orig in graph.neighbors(node_orig):
            neigh = neigh_orig + 1
            neigh_switch_ip = switch_to_ip[neigh]
            link_to_port[neigh_switch_ip][switch_ip] = node 
            link_to_port[switch_ip][neigh_switch_ip] = neigh 

    # set path ips
    for node_i_orig in graph.nodes():
        node_i = node_i_orig + 1
        node_j = node_i + 1
        if (node_j == len(graph.nodes()) + 1):
            node_j = 1
        ecmp_paths = list(islice(nx.all_shortest_paths(graph, node_i_orig, node_j - 1), 7))
        #k_paths = list(islice(nx.shortest_simple_paths(graph, node_i, node_j), 4))

        ecmp_ip_paths = []
        ecmp_ip_rev_paths = []
        for ecmp_path in ecmp_paths:
            ecmp_ip_path = []
            ecmp_ip_rev_path = []
            print "ecmp_path" + str(ecmp_path)
            for i in range(0, len(ecmp_path)):
                ecmp_ip_path.append(switch_to_ip[ecmp_path[i] + 1])
                ecmp_ip_rev_path.insert(0, switch_to_ip[ecmp_path[i] + 1])
            # add end host
            ecmp_ip_path.append(host_to_ip[ecmp_path[len(ecmp_path) - 1] + 1])
            ecmp_ip_rev_path.append(host_to_ip[ecmp_path[0] + 1])
            ecmp_ip_paths.append(ecmp_ip_path)
            ecmp_ip_rev_paths.append(ecmp_ip_rev_path)


        src_ip = host_to_ip[node_i]
        dst_ip = host_to_ip[node_j]
        print "source node: " + str(node_i)
        print "dst node: " + str(node_j)
        print "source ip: " + src_ip
        print "dst ip: " + dst_ip
        print "paths: " + str(ecmp_ip_paths)
        print "reverse paths: " + str(ecmp_ip_rev_paths)
        print ""

        ecmp_path_map[src_ip][dst_ip] = ecmp_ip_paths
        ecmp_path_map[dst_ip][src_ip] = ecmp_ip_rev_paths

    #print ecmp_path_map
    return hosts, ecmp_path_map, link_to_port, ip_to_dpid

def jellyfish_write_paths():
    hosts, ecmp_path_map, link_to_port, ip_to_dpid = jellyfish_graph_to_dicts()
    write_paths(hosts, ecmp_path_map, link_to_port, ip_to_dpid)

def write_paths(hosts, paths, link_to_port, ip_to_dpid):
  # hosts is list of all host IPs
  # paths is [srcip][dstip] -> switch dpids
  # link_to_port is [sw1-dpid][sw2-dpid] -> port
  for src in hosts:
    for dst in hosts:
      paths_list = paths[src][dst]
      for path in paths_list:
        sw1 = None
        for sw2 in path:
          if sw1 is not None:
            port = link_to_port[sw1][sw2]
            if path_map[src][dst][ip_to_dpid[sw1]] is None:
                path_map[src][dst][ip_to_dpid[sw1]] = []
            path_map[src][dst][ip_to_dpid[sw1]].append(port)
            log.debug("pathmap[%s][%s][%d] = %d", src, dst, ip_to_dpid[sw1], port)
          sw1 = sw2

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  jellyfish_write_paths()
  #from proto.arp_responder import launch as arp_launch
  #arp_launch('10.0.0.2=00:00:00:00:00:02', eat_packets=False)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
