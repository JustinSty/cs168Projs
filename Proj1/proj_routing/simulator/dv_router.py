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
    self.table ={} # Each entry in form of [latency(cost), from_which_port, expire_time]


  def update(self, dst, cost):
    self.table[dst] = [cost, port, 0]


  def expire(self, dst):
    del self.table[dst]


  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    for dst in self.table.keys():
      if self.table[dst][1] == port:
        del self.table[dst]


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
      if not dst in self.table or self.table[dst][0] > cost:
        self.update(dst, cost)
    elif isinstance(packet, basics.HostDiscoveryPacket):
      pass
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      self.send(packet, port=self.table[packet.dst][1])

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    # check if any entry expire
    for entry in self.table:
      self.table[entry][2] += DEFAULT_TIMER_INTERVAL
      if self.table[entry][2] >= 15:
        self.expired(entry)
    # send table to all neighbour
    for entry in self.table:
      p = basics.RoutePacket(entry, self.table[entry][0])
      self.send(p, flood=True)







