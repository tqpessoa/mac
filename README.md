# mac
Práticas Engenharia da Computação - CEFET-MG

Parte 1 (Usando a VM)
1) git clone https://github.com/tqpessoa/mac.git

2) cp ~/mac/firewall.csv ~/pox/pox/misc/
O arquivo firewall.csv lista os endereços MACs permitidos

3) cp ~/mac/l2_mac.py ~/pox/pox/
O arquivo l2_mac.py define as regras do firewall

4) File permission: 
chmod 666 ~/pox/pox/misc/firewall.csv

Ativando o controlador:
5) sudo ~/pox/pox.py l2_mac openflow.spanning_tree --no-flood --hold-down log.level --DEBUG samples.pretty_log openflow.discovery host_tracker info.packet_dump      


Parte 2 (Usando SSH):
Utilizando o mininet criar a seguinte topologia:

1) sudo mn --mac --topo single, 10 --controller=remote, ip=127.0.0.1, port=6633

2) Cadastrar no arquivo a lista de MACs liberados 

Parte 3:
Configurar uma topologia em árvore, habilitando o bloqueio por MACs e o bloqueio das Portas 80 e 8080. 
a) Descreva a topoloogia e a suas conexões.
b) Qual o tipo de consulta realizada pelo switch ao controlador? Justifique sua resposta através das tabelas armazenadas.



