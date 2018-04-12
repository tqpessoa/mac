# mac
Práticas Engenharia da Computação - CEFET-MG

Parte 1 (Usando a VM)
1) git clone https://github.com/tqpessoa/mac.git

2) cp ~/mac/l2_firewall.py ~/pox/ext/
O arquivo l2_firewall.py define as regras do firewall


Ativando o controlador:
1) sudo ~/pox/pox.py l2_firewall log.level --DEBUG samples.pretty_log openflow.discovery host_tracker info.packet_dump      


Parte 2 (Usando SSH):
Utilizando o mininet criar a seguinte topologia:

1) sudo mn --mac --topo single, 10 --controller=remote, ip=127.0.0.1, port=6633

2) Cadastrar no arquivo a lista de MACs liberados 

Parte 3:
Configurar uma topologia em árvore, habilitando o bloqueio por MACs e o bloqueio das Portas 80 e 8080. 


a) Descreva a topoloogia e a suas conexões.


b) Qual o tipo de consulta realizada pelo switch ao controlador? Justifique sua resposta através das tabelas armazenadas.



