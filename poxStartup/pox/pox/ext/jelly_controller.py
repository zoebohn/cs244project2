# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's roughly similar to the one Brandon Heller did for NOX.
"""

from heapq import heappush, heappop
from itertools import count
from pox.core import core
from mininet.log import setLogLevel
from pox.lib.util import dpidToStr
import pox.ext.ripl_routing as ripl
import pox.ext.build_topology as topo
import pox.openflow.libopenflow_01 as of
import networkx as nx
import json

log = core.getLogger()
#setLogLevel('info')


class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}

    self.switches = {}

    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    self.graph = nx.readwrite.node_link_graph(data)

    self.t = topo.JellyFishTop()
    self.r = ripl.STStructuredRouting(self.t)

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


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """
    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    if packet.src not in self.mac_to_port:
        self.mac_to_port[packet.src] = packet_in.in_port 

    if packet.dst in self.mac_to_port:
      # Send packet out the associated port
      self.resend_packet(packet_in, self.mac_to_port[packet.dst])

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

      log.debug("Installing flow...")
      # Maybe the log statement should have source/destination/port?

#      msg = of.ofp_flow_mod()
      #
      ## Set fields to match received packet
#      msg.match = of.ofp_match.from_packet(packet)
      #
      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      #
      #< Add an output action, and send -- similar to resend_packet() >
#      msg.data = packet_in

      # Add an action to send to the specified port
#      action = of.ofp_action_output(port = self.mac_to_port[packet.dst])
#      msg.actions.append(action)

      # Send message to switch
#      self.connection.send(msg)

    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)

  def _install_proactive_flows(self):
    t = self.t
    # Install L2 src/dst flow for every possible pair of hosts.
    for src in sorted(self._raw_dpids(t.g.nodes())):
      for dst in sorted(self._raw_dpids(t.g.nodes())):
        self._install_proactive_path(src, dst)

  def _install_proactive_path(self, src, dst):
    """Install entries on route between two hosts based on MAC addrs.
    
    src and dst are unsigned ints.
    """
    src_sw = self.t.up_nodes(self.t.id_gen(dpid = src).name_str())
    assert len(src_sw) == 1
    src_sw_name = src_sw[0]
    dst_sw = self.t.up_nodes(self.t.id_gen(dpid = dst).name_str())
    assert len(dst_sw) == 1
    dst_sw_name = dst_sw[0]
    hash_ = self._src_dst_hash(src, dst)
    route = self.r.get_route(src_sw_name, dst_sw_name, hash_)
    log.info("route: %s" % route)

    # Form OF match
    match = of.ofp_match()
    match.dl_src = EthAddr(src).toRaw()
    match.dl_dst = EthAddr(dst).toRaw()

    dst_host_name = self.t.id_gen(dpid = dst).name_str()
    final_out_port, ignore = self.t.port(route[-1], dst_host_name)
    for i, node in enumerate(route):
      node_dpid = self.t.id_gen(name = node).dpid
      if i < len(route) - 1:
        next_node = route[i + 1]
        out_port, next_in_port = self.t.port(node, next_node)
      else:
        out_port = final_out_port
      self.switches[node_dpid].install(out_port, match)


  def install(self, port, match, buf = -1, idle_timeout = 0, hard_timeout = 0,
              priority = of.OFP_DEFAULT_PRIORITY):
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.idle_timeout = idle_timeout
    msg.hard_timeout = hard_timeout
    msg.priority = priority
    msg.actions.append(of.ofp_action_output(port = port))
    msg.buffer_id = buf
    self.connection.send(msg)

  def _raw_dpids(self, arr):
    "Convert a list of name strings (from Topo object) to numbers."
    return [self.t.id_gen(name = a).dpid for a in arr]  

  def _flood(self, event):
    packet = event.parsed
    dpid = event.dpid
    #log.info("PacketIn: %s" % packet)
    in_port = event.port
    t = self.t

    # Broadcast to every output port except the input on the input switch.
    # Hub behavior, baby!
    for sw in self._raw_dpids(t.g.nodes()):
      #log.info("considering sw %s" % sw)
      ports = []
      sw_name = t.id_gen(dpid = sw).name_str()
      for host in t.down_nodes(sw_name):
        sw_port, host_port = t.port(sw_name, host)
        if sw != dpid or (sw == dpid and in_port != sw_port):
          ports.append(sw_port)
      # Send packet out each non-input host port
      # TODO: send one packet only.
      for port in ports:
        #log.info("sending to port %s on switch %s" % (port, sw))
        #buffer_id = event.ofp.buffer_id
        #if sw == dpid:
        #  self.switches[sw].send_packet_bufid(port, event.ofp.buffer_id)
        #else:
        self.switches[sw].send_packet_data(port, event.data)
        #  buffer_id = -1 

  def _handle_packet_proactive(self, event):
    packet = event.parse()

    if packet.dst.isMulticast():
      self._flood(event)
    else:
      dpids = self._raw_dpids(self.t.g.nodes())
      if packet.src.toInt() not in dpids:
        raise Exception("unrecognized src: %s" % packet.src)
      if packet.dst.toInt() not in dpids:
        raise Exception("unrecognized dst: %s" % packet.dst)
      raise Exception("known host MACs but entries weren't pushed down?!?")

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    print "Src: " + str(packet.src)
    print "Dest: " + str(packet.dst)
    print "Event port: " + str(event.port)
    #self.act_like_hub(packet, packet_in)
    log.info("packet in")
    #self.act_like_switch(packet, packet_in)
    self._handle_packet_proactive(event)

  def _handle_ConnectionUp(self, event):
    sw = self.switches.get(event.dpid)
    sw_str = dpidToStr(event.dpid)
    log.info("Saw switch come up: %s", sw_str)
    name_str = self.t.id_gen(dpid = event.dpid).name_str()
    if name_str not in self.t.switches():
      log.warn("Ignoring unknown switch %s" % sw_str)
      return
    if sw is None:
      log.info("Added fresh switch %s" % sw_str)
      sw = Switch()
      self.switches[event.dpid] = sw
      sw.connect(event.connection)
    else:
      log.info("Odd - already saw switch %s come up" % sw_str)
      sw.connect(event.connection)
    sw.connection.send(of.ofp_set_config(miss_send_len=MISS_SEND_LEN))

    if len(self.switches) == len(self.t.switches()):
      log.info("Woo!  All switches up")
      self.all_switches_up = True
      self._install_proactive_flows()

def launch ():
  """
  Starts the component
  """
  #setLogLevel('info')
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
