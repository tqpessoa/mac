# mac
Práticas Engenharia da Computação - CEFET-MG

Parte 1 (Usando a VM)
1) git clone https://github.com/tqpessoa/mac.git

cp ~/NodePI/port.csv ~/pox/pox/misc/ #cp ~/NodePI/firewall.csv ~/pox/pox/misc/
Change file permission: # chmod 666 ~/pox/pox/misc/port.csv # chmod 666 ~/pox/pox/misc/cavfirewall.csv

Ativando o controlador:
sudo ~/pox/pox.py l2_mac openflow.spanning_tree --no-flood --hold-down log.level --DEBUG samples.pretty_log openflow.discovery host_tracker info.packet_dump      


Parte 2 (Usando SSH):
Utilizando o mininet criar a seguinte topologia:

1) sudo mn --mac --topo single, 10 --controller=remote, ip=127.0.0.1, port=6633

