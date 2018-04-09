
# Based on l2_learning.py by James McCauley
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


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time
from pox.lib.addresses import EthAddr
from pox.lib.addresses import IPAddr
from collections import namedtuple
import os

log = core.getLogger()

_flood_delay = 0

policyFile = "%s/pox/pox/misc/csvfirewall.csv"  % os.environ[ 'HOME' ]

''' Importa lista de MAC Cadastrados '''

#busca macs cadastrados

allowmacs = []
fp = open(policyFile)
line = fp.readline() #ignore first line
line = fp.readline()
while line:
    item = line.split(',')
    item[0] = int(item[0])
    item[2] = item[2].strip() #remove white space
    allowmacs.append(item)
    print item[0], item[1], item[2]
    line = fp.readline()
fp.close()


class LearningSwitch (object):
 
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Tabela Mac
    self.macToPort = {}

    # Tabela Firewall
    self.firewall = {}

    # Adiciona Regras 
   
    for item in allowmacs:
            print item[1]
            print item[2]
	    self.AddRule((item[1]),EthAddr(item[2]))	 
   log.debug("Firewall - Regras instaladas")
   
    # Ouvir mensagens de entrada
    connection.addListeners(self)
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))


  #Função que permite adicionar regras de firewall na tabela de firewall
  def AddRule (self, dpidstr, src=0,value=True):
    self.firewall[(dpidstr,src)]=value
    log.debug("Adding firewall rule in %s: %s", dpidstr, src) 

  #Função que permite excluir regras de firewall da tabela de firewall
  def DeleteRule (self, dpidstr, src=0):
     try:
       del self.firewall[(dpidstr,src)]
       log.debug("Deleting firewall rule in %s: %s",
                 dpidstr, src)
     except KeyError:
       log.error("Cannot find in %s: %s",
                 dpidstr, src)


  # Verificar se o pacote está em conformidade com as regras antes de prosseguir
  def CheckRule (self, dpidstr, src=0):
    try:
      entry = self.firewall[(dpidstr, src)]
      if (entry == True):
        log.debug("Rule (%s) found in %s: FORWARD",
                  src, dpidstr)
      else:
        log.debug("Rule (%s) found in %s: DROP",
                  src, dpidstr)
      return entry
    except KeyError:
      log.debug("Rule (%s) NOT found in %s: DROP",
                src, dpidstr)
      return False

  def _handle_PacketIn (self, event):
    """
    Manipular o pacote em mensagens do switch para implementar o algoritmo acima
    """

    packet = event.parsed

    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        

        if self.hold_down_expired is False:
         
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      """
      Drops este pacote e, opcionalmente, instala um fluxo para continuar
      dropping similares por um tempo
      """
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port # 1

    # Obter o DPID da Switch Connection
    dpidstr = dpid_to_str(event.connection.dpid)

    # Regras Firewall
    if self.CheckRule(dpidstr, packet.src) == False:
      drop()
      return

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        # 6
        log.debug("installing flow for %s.%i -> %s.%i" %
                  (packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)


class l2_learning (object):
  """
  Aguardando switches openflow .
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay):
  """
  Start  o switch L2 learning.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
