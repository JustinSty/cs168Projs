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
    self.neighbour = {} # port:ping to neighbour
    self.table = {} # dst:[port, total cost, time]
    self.e_table = {}


  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.neighbour[port] = latency;
    for dst in self.table.keys():
      p = basics.RoutePacket(dst, self.table[dst][1])
      self.send(p, port)


  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    if port in self.neighbour.keys():
      del self.neighbour[port]

    if self.POISON_MODE:
      for dst in self.table.keys():
        if self.table[dst][0] == port:
          #poison table[dst] to a random non-host, with INFINITY cost
          p = basics.RoutePacket(dst, INFINITY)
          self.send(p, flood = True)
          del self.table[dst]
          if dst in self.e_table.keys():
            del self.e_table[dst]

    else:
      remove = []
      for dst in self.table.keys():
        if self.table[dst][0] == port:
          remove.append(dst)

      for dst in remove:
        del self.table[dst]
        if dst in self.e_table.keys():
          del self.e_table[dst]

      for dst in self.table.keys():
        p = basics.RoutePacket(dst, self.table[dst][1])
        self.send(p, flood=True)


  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    if isinstance(packet, basics.RoutePacket):
      dst = packet.destination
      cost = packet.latency

      #when receive poison, poison reverse
      if self.POISON_MODE and cost == INFINITY:
        for tar_dst in self.table.keys():
          if self.table[tar_dst][0] == port:
            self.table[tar_dst] = [self.table[tar_dst][0], INFINITY, self.table[tar_dst][2]]

      #when new route/shortest path established
      if (dst not in self.table.keys()) or ((self.neighbour[port] + cost) < self.table[dst][1]):
        self.table[dst] = [port, self.neighbour[port] + cost, 0]
        p = basics.RoutePacket(dst, self.table[dst][1])
        self.send(p, port, flood = True)

      #when receive a shortest route became longer
      if (dst in self.table.keys()) and (self.table[dst][0] == port) and (self.table[dst][1] < cost + self.neighbour[port]):
        new_cost = cost + self.neighbour[port]
        self.table[dst] = [port, cost + self.neighbour[port], 0]
        p = basics.RoutePacket(dst, self.table[dst][1])
        self.send(p, port, flood = True)


    elif isinstance(packet, basics.HostDiscoveryPacket):
      self.table[packet.src] = [port, self.neighbour[port], 0]

      #send whole table to all neighbour except PORT
      for tar_dst in self.table.keys():
        p = basics.RoutePacket(tar_dst, self.table[tar_dst][1])
        self.send(p, port, flood = True)

    else:
      if (packet.dst in self.table.keys()):
        self.send(packet, self.table[packet.dst][0])
      elif (packet.dst in self.e_table.keys()):
        self.send(packet, self.e_table[packet.dst][0])
      else:
        #if received a PACKET thats has no route in table
        #send to a random non-host link
        sent = 0
        host_port = []
        for tar_dst in self.table.keys():
          if self.table[tar_dst][0] in self.neighbour.keys() and self.table[tar_dst][1] == self.neighbour[self.table[tar_dst][0]]:
            host_port.append(self.table[tar_dst][0])

        for p in self.neighbour.keys():
          if not p in host_port:
            self.send(packet, p)
            sent = 1
            break
        #should not happen
        if sent == 0:
          print("send back")
          self.send(packet, port)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    # check if any entry expire.
    expire = []
    for dst in self.table.keys():
      self.table[dst][2] += self.DEFAULT_TIMER_INTERVAL
      if self.table[dst][2] >= 15:
        expire.append(dst)

    for dst in expire:
      if self.table[dst][0] in self.neighbour.keys() and self.neighbour[self.table[dst][0]] == self.table[dst][1]:
        self.table[dst] = [self.table[dst][0], self.table[dst][1], 0]
      else:
        self.e_table[dst] = [self.table[dst][0], self.table[dst][1]]
        del self.table[dst]


    # send table to all neighbour except that using
    for dst in self.table.keys():
        for port in self.neighbour.keys():
          if not port == self.table[dst][0]:
            p = basics.RoutePacket(dst, self.table[dst][1])
            self.send(p, port)





