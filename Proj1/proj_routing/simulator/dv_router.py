"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  #POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    self.table1 = {} # port:ping to neighbour
    self.table2 = {} # dst:[port, total cost, time]



  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.table1[port] = latency;

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    if port in self.table1.keys():
      del self.table1[port]


  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())
    if isinstance(packet, basics.RoutePacket):
      dst = packet.destination
      cost = packet.latency 
      #assuming link must be recorded already
      if (dst not in self.table2.keys()) or ((self.table1[port] + cost) < self.table2[dst][1]):
        self.table2[dst] = [port, self.table1[port] + cost, 0]

      #send table to all neighbours except PORT
      for tar_dst in self.table2.keys():
        for tar_port in self.table1.keys():
          if not tar_port == port:
            p = basics.RoutePacket(tar_dst, self.table2[tar_dst][1])
            self.send(p, tar_port)

    elif isinstance(packet, basics.HostDiscoveryPacket):
      print('HostDiscoveryPacket')
      self.table2[packet.src] = [port, self.table1[port], 0]    #???

      for tar_dst in self.table2.keys():
        for tar_port in self.table1.keys():
          if not tar_port == port:
            p = basics.RoutePacket(tar_dst, self.table2[tar_dst][1])
            self.send(p, tar_port)
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      if (packet.dst in self.table2.keys()):
        self.send(packet, self.table2[packet.dst])
      else:
        self.send(packet, port)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    # check if any entry expire.
    expire = []
    for dst in self.table2:
      self.table2[dst][2] += self.DEFAULT_TIMER_INTERVAL
      if self.table2[dst][2] >= 15:
        #expire.append(dst)
        pass

    for dst in expire:
      if self.table1[self.table2[dst][0]] == self.table2[dst][1]:
        self.table2[dst][2] = 0
      else:
        del self.table2[dst]

      print("del")             
    # send table to all neighbour

    for dst in self.table2.keys():
      p = basics.RoutePacket(dst, self.table2[dst][1])
      self.send(p, flood = True)





