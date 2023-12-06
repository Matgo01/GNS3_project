
from gns3fy import Gns3Connector, Project
from Dos_attack import dos_attack
from TCP_SYN_flood_attack import attack
from TCP_ACK_flood_attack import tcp_ack_floos
from UDP_attack import attack_udp
#indirizzo del server gns3
gns3_server="http://192.168.105.130:80"

#nome del progetto gns3
project_name="myProject_matteo_mt"

#creazione di una connessione al server gns3
gns3=Gns3Connector(gns3_server)

#verifico se il progetto esiste gia
#project=Project.list(gns3)
#if "myProject_matteo2.0" in project:
    #print("il progetto esiste")
project=Project(name=project_name,connector=gns3)
#else:
    #print("il progetto non eiste")
project.get()
print(len(project.nodes))
#attivo la simulazione
#assegno ad una variabile il nodo e lo starto per manipolarlo
node_1=project.nodes[0]
node_2=project.nodes[1]
node_3=project.nodes[2]
node_4=project.nodes[3]
node_5=project.nodes[4]
node_6=project.nodes[5]
#stampo lo stato iniziale dei nodi
print(node_1.status)
print(node_2.status)
print(node_3.status)
print(node_4.status)
print(node_5.status)
print(node_6.status)
#attivo i nodi  e stampo il loro stato
node_1.start()
print(node_1.status)
node_2.start()
print(node_2.status)
node_3.start()
print(node_3.status)
node_4.start()
print(node_4.status)
node_5.start()
print(node_5.status)
node_6.start()
print(node_6.status)
#eseguo i vari attacchi dos sullo switch all'interno del progetto gns3
#ottengo l'indirizzo e la porta dello switch
# l'indirizzo IP del nodo_1
switch_ip ="192.168.56.130"
#  la porta del nodo_1
switch_port = 5000
# Stampa l'indirizzo IP e la porta dello switch
print(f"Indirizzo IP del nodo_1: {switch_ip}")
print(f"Porta del nodo_1: {switch_port}")
dos_attack(switch_ip,switch_port)
attack(switch_ip,switch_port)
tcp_ack_floos(switch_ip,switch_port)
attack_udp(switch_ip)
print(f"attacco dos attivato sullo switch{switch_ip}:{switch_port} nel progetto {project_name}")
