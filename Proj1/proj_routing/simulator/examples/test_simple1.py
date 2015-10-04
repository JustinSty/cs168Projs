"""
A simple test

Creates some hosts connected to a single central switch/router.
Sends some pings.
Makes sure the right number of pings reach expected destinations and no pings
reach unexpected destinations.
"""

import sim
import sim.api as api
import sim.basics as basics


class GetPacketHost (basics.BasicHost):
  """
  A host that expects to see a ping
  """
  pings = 0
  def handle_rx (self, packet, port):
    if isinstance(packet, basics.Ping):
      self.pings += 1


class NoPacketHost (basics.BasicHost):
  """
  A host that expects to NOT see a ping
  """
  bad_pings = 0
  def handle_rx (self, packet, port):
    if isinstance(packet, basics.Ping):
      NoPacketHost.bad_pings += 1


def launch ():
  h1 = GetPacketHost.create("h1")
  h2 = NoPacketHost.create("h2")
  h3 = NoPacketHost.create("h3")
  h4 = GetPacketHost.create("h4")
  h5 = GetPacketHost.create("h5")

  r0 = sim.config.default_switch_type.create("r0")
  r1 = sim.config.default_switch_type.create("r1")
  r2 = sim.config.default_switch_type.create("r2")
  r3 = sim.config.default_switch_type.create("r3")
  r4 = sim.config.default_switch_type.create("r4")
  r5 = sim.config.default_switch_type.create("r5")

  r0.linkTo(r1)
  r1.linkTo(r2)
  r2.linkTo(r3)
  r3.linkTo(r4)
  r4.linkTo(r5)
  r5.linkTo(r1)
  r1.linkTo(h1)
  r2.linkTo(h2)
  r3.linkTo(h3)
  r4.linkTo(h4)
  r5.linkTo(h5)


  def test_tasklet ():
    yield 5 # Wait five seconds for routing to converge

    api.userlog.debug("Sending test pings")

    yield 1
    #r1.unlinkTo(r2)
    h2.ping(h4)
    h2.ping(h1)

    yield 1 # Wait a bit before sending last ping

    h3.ping(h1)


    yield 1
    h4.ping(h5)

    yield 1
    h1.ping(h4)

    yield 1
    h2.ping(h4)

    yield 1
    h3.ping(h4)

    yield 1
    h4.ping(h4)

    yield 1
    h5.ping(h4)

    yield 1
    h1.ping(h4)

    yield 1
    h2.ping(h4)

    yield 1
    h3.ping(h4)

    yield 1
    h4.ping(h4)

    yield 1
    h5.ping(h4)


    yield 8 # Wait five seconds for pings to be delivered

    good = True
    if h1.pings != 2:
      api.userlog.error("h1 got %s packets instead of 2", h1.pings)
      good = False
    if h4.pings != 11:
      api.userlog.error("h4 got %s packets instead of 11", h4.pings)
      good = False
    if h5.pings != 1:
      api.userlog.error("h5 got %s packets instead of 1", h5.pings)
      good = False
    if NoPacketHost.bad_pings != 0:
      api.userlog.error("Got %s unexpected packets", NoPacketHost.bad_pings)
      good = False

    if good:
      api.userlog.debug("Test passed successfully!")

    # End the simulation and (if not running in interactive mode) exit.
    import sys
    sys.exit(0)

  api.run_tasklet(test_tasklet)
