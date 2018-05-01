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
import pox.openflow.libopenflow_01 as of
import networkx as nx
import json

log = core.getLogger()



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

    with open('generated_rrg', 'r') as infile:
        data = json.load(infile)
    self.graph = nx.readwrite.node_link_graph(data)

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

  def k_shortest_paths(source, target, k=1, weight='weight'):
    """Returns the k-shortest paths from source to target in a weighted graph G.
    Parameters
    ----------
    source : node
       Starting node
    target : node
       Ending node
       
    k : integer, optional (default=1)
        The number of shortest paths to find
    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight
    Returns
    -------
    lengths, paths : lists
       Returns a tuple with two lists.
       The first list stores the length of each k-shortest path.
       The second list stores each k-shortest path.  
    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.
    Examples
    --------
    >>> G=nx.complete_graph(5)    
    >>> print(k_shortest_paths(G, 0, 4, 4))
    ([1, 2, 2, 2], [[0, 4], [0, 1, 4], [0, 2, 4], [0, 3, 4]])
    Notes
    ------
    Edge weight attributes must be numerical and non-negative.
    Distances are calculated as sums of weighted edges traversed.
    """
    if source == target:
        return ([0], [[source]]) 
       
    G = self.graph.copy()
    length, path = nx.single_source_dijkstra(G, source, target, weight=weight)
    if target not in length:
        raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))
        
    lengths = [length[target]]
    paths = [path[target]]
    c = count()        
    B = []                        
    G_original = G.copy()    
    
    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):            
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]
            
            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G.has_edge(u, v):
                        edge_attr = G.edge[u][v]
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            
            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for u, v, edge_attr in G.edges_iter(node, data=True):
                    G.remove_edge(u, v)
                    edges_removed.append((u, v, edge_attr))
                
                if G.is_directed():
                    # in-edges
                    for u, v, edge_attr in G.in_edges_iter(node, data=True):
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            
            spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, target, weight=weight)            
            if target in spur_path and spur_path[target]:
                total_path = root_path[:-1] + spur_path[target]
                total_path_length = get_path_length(G_original, root_path, weight) + spur_path_length[target]                
                heappush(B, (total_path_length, next(c), total_path))
                
            for e in edges_removed:
                u, v, edge_attr = e
                G.add_edge(u, v, edge_attr)
                       
        if B:
            (l, _, p) = heappop(B)        
            lengths.append(l)
            paths.append(p)
        else:
            break
    
    return (lengths, paths)  


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
    self.act_like_switch(packet, packet_in)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
