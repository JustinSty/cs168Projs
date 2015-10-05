"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    self.neighbour = {} # port:latency to neighbour
    self.hosts = [] # port that connects to host
    self.table = {} # dst:[port, total cost, time, valid_bit]


  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.neighbour[port] = latency
    for dst in self.table:
      p = basics.RoutePacket(dst, self.table[dst][1])
      self.send(p, port=port)


  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    if port in self.neighbour:
      del self.neighbour[port]

    expiredEntries = []
    for dst in self.table:
      if self.table[dst][0] == port:
        expiredEntries.append(dst)

    for dst in expiredEntries:
      del self.table[dst]
      if self.POISON_MODE:
        p = basics.RoutePacket(dst, INFINITY)
        self.send(p, flood=True)


  def update(self, dst, port, cost):
    """
    Called by self.handle_rx() when a entry in the table need to be updated.

    arguments
    dst - destination
    port - from which neighbour
    cost - latency to destination
    """
    self.table[dst] = [port, cost, api.current_time()]
    p = basics.RoutePacket(dst, cost)
    self.send(p, port=port, flood=True)
    if self.POISON_MODE:
      p = basics.RoutePacket(dst, INFINITY)
      self.send(p, port=port)


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
      cost = packet.latency + self.neighbour[port]
      if packet.latency == INFINITY and self.POISON_MODE:
        if dst in self.table and self.table[dst][0] == port:
          del self.table[dst]
          p = basics.RoutePacket(dst, INFINITY)
          self.send(p, flood=True)
      elif dst not in self.table or cost < self.table[dst][1]:
        self.update(dst, port, cost)
      # trust neighbour
      elif port == self.table[dst][0] and cost > self.table[dst][1]:
        self.update(dst, port, cost)
      elif port == self.table[dst][0] and cost == self.table[dst][1]:
        self.table[dst][2] = api.current_time()

    elif isinstance(packet, basics.HostDiscoveryPacket):
      self.hosts.append(port)
      dst = packet.src
      cost = self.neighbour[port]
      self.update(dst, port, cost)

    else:
      dst = packet.dst
      if dst in self.table and not self.table[dst][1] == INFINITY and self.table[dst][0] != port:
        self.send(packet, self.table[packet.dst][0])


  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    # check if any entry expire.
    expiredEntries = []
    for dst in self.table:
      # leave the entry of host unchanged
      if self.table[dst][0] not in self.hosts and api.current_time() - self.table[dst][2] >= 15:
        expiredEntries.append(dst)
    for dst in expiredEntries:
      del self.table[dst]
      if self.POISON_MODE:
        p = basics.RoutePacket(dst, INFINITY)
        self.send(p, flood=True)

    # send table to neighbours.
    for dst in self.table:
      p = basics.RoutePacket(dst, self.table[dst][1])
      self.send(p, port=self.table[dst][0], flood=True)



