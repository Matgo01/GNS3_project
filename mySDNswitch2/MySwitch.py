#!/usr/bin/env python3
import asyncio
import time
import psutil as psutil
from ovs.db import idl
from ovs import jsonrpc
from scapy.layers.l2 import Ether, ARP
from scapy.sendrecv import srp


class MySwitch:

    def __init__(self,name, bridge_name, controller_ip, controller_port):
        """
        Inizializza un oggetto MySwitch con il nome del bridge, l'indirizzo IP e la porta del controller OpenFlow.

        :param bridge_name: Nome del bridge.
        :param controller_ip: Indirizzo IP del controller OpenFlow.
        :param controller_port: Porta del controller OpenFlow.
        """
        self.idl_ = None
        self.bridge_name = bridge_name
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.name = name
        self.conn = None
        self.flows = []
        self.interfaces = ["en0", "en1", "en3","en4","en5","en6"]
        self.network_prefix = 'localhost'
        # Aggiungo una tabella per gli indirizzi IP e MAC
        self.ip_mac_table = {}
        # Attributo per memorizzare l'ultimo pacchetto e la porta di ingresso
        self.last_packet = None
        self.last_in_port = None
    def connect(self):
        """
        Apre una connessione con lo switch.
        """
        try:
            connection = jsonrpc.Connection("unix:/var/run/openvswitch/db.sock")
            idl_ = idl.Idl(connection, schema_helper=None)
            self.conn = idl_
            # Configura il controller OpenFlow
            bridge = self.conn.tables['Bridge'].rows.get(self.bridge_name)
            controller = bridge.ensure_column('controller')
            controller[0] = 'tcp:{}:{}'.format(self.controller_ip, self.controller_port)
        #Applicare le modifiche
            self.idl_.commit_block()
        except Exception as e:
         print(f"Errore durante la connessione: {e}")

    def close(self):
        """
               Chiude la connessione con lo switch.
               """
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Errore durante la chiusura della connessione: {e}")

    def get_ports(self):
        """
        Restituisce un elenco delle porte dello switch.

        :return: Elenco delle porte dello switch.
        """
        if not self.conn:
            raise ValueError("La connessione non è aperta.")

        with self.conn as conn:
            return [conn.get_port(port) for port in conn.get_ports()]

    def get_links(self):
        """
        Restituisce un elenco dei link dello switch.

        :return: Elenco dei link dello switch.
        """
        if not self.conn:
            raise ValueError("La connessione non è aperta.")

        with self.conn as conn:
            return [conn.get_link(link) for link in conn.get_links()]

    def get_flows(self):
        """
        Restituisce un elenco dei flussi dello switch.

        :return: Elenco dei flussi dello switch.
        """
        if not self.conn:
            raise ValueError("La connessione non è aperta.")

        with self.conn as conn:
            return [conn.get_flow(flow) for flow in conn.get_flows()]

    def set_link_bandwidth(self, link_name, bandwidth):
     try:
         # Imposta la larghezza di banda del link nel database Open vSwitch
        link = self.conn.tables['Interface'].rows.get(link_name)
        link.ensure_column('ingress_policing_rate')[0] = bandwidth
        self.conn.commit_block()

     except Exception as e:
        print(f"Errore durante la configurazione della larghezza di banda del link: {e}")

    def send_message(self, message):
      try:

        # Invia un messaggio
        print(f"Sending message: {message}")

      except Exception as e:
            print(f"Errore durante l'invio del messaggio: {e}")

    def wait_for_config_apply(self):
      try:
        #  Attendere l'applicazione della configurazione
        time.sleep(20)
        print("Waiting for configuration to be applied")

      except Exception as e:
        print(f"Errore durante l'attesa dell'applicazione della configurazione: {e}")

    def get_traffic_data(self):
     try:
        # Ottenere le statistiche di rete
        net_stats = psutil.net_io_counters(pernic=True)

        traffic_data = {}
        for interface_name, stats in net_stats.items():
            interface_data = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,

            }
            traffic_data[interface_name] = interface_data

        return traffic_data

     except Exception as e:
        print(f"Errore durante l'ottenimento dei dati sul traffico: {e}")
        return None


    def get_info(self):
     """
               Ottiene informazioni sullo switch.

               :return: Dizionario contenente le informazioni dello switch.
               """
     info = {
        'name': self.name,
        'bridge_name': self.bridge_name,
        'controller_ip': self.controller_ip,
        'controller_port': self.controller_port,
        # Aggiungi altri attributi che desideri includere nelle informazioni dello switch
    }
     return info

    def add_flow(self, in_port, out_port, actions):
        # Logica per aggiungere un flusso
        flow = {'in_port': in_port, 'out_port': out_port, 'actions': actions}
        self.flows.append(flow)

    async def get_mac_address(self, ip, interface):
        """
        Ottiene l'indirizzo MAC associato a un indirizzo IP su una specifica interfaccia.
        """
        try:
            # Creaziono del pacchetto ARP richiedendo l'indirizzo MAC per l'indirizzo IP specificato
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)

            # Invio del pacchetto ARP e ricezione della risposta
            result = await asyncio.to_thread(srp, arp_request, timeout=3, iface=interface, verbose=False)

            # Estrai l'indirizzo MAC dalla risposta
            mac_address = result[0][1].hwsrc

             # Aggiorno la tabella degli indirizzi MAC
            self.ip_mac_table[ip] = mac_address

            return mac_address
        except Exception as e:
            print(f"Errore durante l'ottenimento dell'indirizzo MAC: {e}")
            return None

    async def scan_network(self):
        """
        Scansiona tutti gli indirizzi IP nella rete locale per ottenere gli indirizzi MAC.
        """
        tasks = []

        #  range di indirizzi IP della rete
        for i in range(1, 255):
            ip_address = f"{self.network_prefix}.{i}"
            for interface in self.interfaces:
                tasks.append(self.get_mac_address(ip_address, interface))

        mac_addresses = await asyncio.gather(*tasks)

        for interface, mac_address in zip(self.interfaces, mac_addresses):
            if mac_address:
                print(f"Indirizzo MAC su {interface}: {mac_address}")
            else:
                print(f"Impossibile ottenere l'indirizzo MAC su {interface}.")


    async def process_packet(self):
        """
        Processa l'ultimo pacchetto ricevuto.
        """
        try:
            if self.last_packet and self.last_in_port is not None:
                # Estrai l'indirizzo MAC di destinazione dal pacchetto
                dst_mac = self.last_packet.dst

                # Verifica se conosco l'associazione IP-MAC
                if dst_mac in self.ip_mac_table.values():
                    # Trovo l'indirizzo IP associato all'indirizzo MAC di destinazione
                    ip_dest = next(ip for ip, mac in self.ip_mac_table.items() if mac == dst_mac)

                    # Trovo la porta associata all'indirizzo IP nella tabella delle porte
                    with self.conn as conn:
                        port_dest = conn.get_port_by_ip(ip_dest)

                    # Inoltra il pacchetto alla porta di destinazione
                    print(f"Forwarding packet to port {port_dest}")

                else:
                    # Caso di flood: inoltra il pacchetto a tutte le porte tranne quella di ingresso
                    all_ports = self.get_ports()
                    all_ports.remove(self.last_in_port)
                    print(f"Flooding packet to all ports except {self.last_in_port}")

        except Exception as e:
            print(f"Errore durante l'instradamento del pacchetto: {e}")






    def start_and_monitor_traffic(self):
        try:
            # Connessione allo switch
            self.connect()


            # Ciclo di monitoraggio del traffico
            while True:
                # Ottieni dati sul traffico
                traffic_data = self.get_traffic_data()
                for interface_name, data in traffic_data.items():
                    print(f"Interface: {interface_name}")
                    print(f"Bytes Sent: {data['bytes_sent']}")
                    print(f"Bytes Received: {data['bytes_recv']}")
                    print(f"Packets Sent: {data['packets_sent']}")
                    print(f"Packets Received: {data['packets_recv']}")
                    print("\n")

                # stampa dati traffico
                print("Traffic Data:", traffic_data)

                #  ritardo prima di ottenere nuovi dati
                time.sleep(5)  # Aspetta 5 secondi prima di ottenere nuovi dati

        except KeyboardInterrupt:
            # Gestisco l'interruzione dell'utente (CTRL+C) per interrompere il ciclo
            pass
        except Exception as e:
            print(f"Errore durante il monitoraggio del traffico: {e}")
        finally:
            # Chiudo la connessione allo switch quando il ciclo è interrotto
            self.close()

# Creo un'istanza di MySwitch con i parametri desiderati
my_switch = MySwitch(name="Switch1", bridge_name="br0", controller_ip="127.0.0.1", controller_port=90)

# Avvio e monitoro lo switch
my_switch.start_and_monitor_traffic()
my_switch.scan_network()
my_switch.process_packet()
