from Link import Link

class Sensor:
    def __init__(self, name, type, protocol):
        """
        Inizializza un oggetto Sensor con un nome, un tipo e un protocollo.

        :param name: Nome del sensore.
        :param type: Tipo di sensore.
        :param protocol: Protocollo utilizzato dal sensore.
        """
        self.name = name
        self.type = type
        self.protocol = protocol
        self.data = {}  # Dizionario per memorizzare i dati dei link
        self.traffic_data = []

    def collect_data(self, switches):
        """
        Raccoglie dati sul traffico dalle porte degli switch.

        :param switches: Dizionario di switch con nome come chiave.
        """
        for switch in switches.values():
            switch_info = switch.get_info()
            for port in switch_info.ports:
                if port.state in ["UDP", "TCP", "HTTPS", "MQTT"]:
                    port_stats = switch.get_port_stats(port.name)
                    link = Link(port.name, switch_info.name, port.peer_name, self.name)
                    link.bandwidth_usage = port_stats.bytes / port_stats.duration
                    self.data[link.name] = link

    def collect_traffic_data_router(self, traffic_data):
        """
        Aggiunge dati di traffico dalla struttura dati del router al sensore.

        :param traffic_data: Dati di traffico dal router.
        """
        for interface in traffic_data.interfaces:
            link_name = interface.name
            bandwidth_usage = interface.in_bytes / interface.duration
            link = Link(link_name, None, self.name, None)
            link.bandwidth_usage = bandwidth_usage
            traffic_data.links.append(link)

    def collect_traffic_data_firewall(self, traffic_data):
        """
        Aggiunge dati di traffico dalla struttura dati del firewall al sensore.

        :param traffic_data: Dati di traffico dal firewall.
        """
        for rule in traffic_data.rules:
            link_name = rule.name
            bandwidth_usage = rule.in_bytes / rule.duration
            link = Link(link_name, None, self.name, None)
            link.bandwidth_usage = bandwidth_usage
            traffic_data.links.append(link)

    def notify_controller(self, congested_links):
        """
        Notifica il controller sulla congestione dei link.

        :param congested_links: Lista di link congestionati.
        """
        message = f"congestione rilevata nei seguenti link: {','.join(congested_links)}"
        print(message)  # Sostituisci con la tua logica per inviare il messaggio al controller

    def get_data(self, switch_name):
        """
        Restituisce i dati del link associato a uno switch.

        :param switch_name: Nome dello switch.
        :return: Oggetto Link o lista vuota se non ci sono dati disponibili.
        """
        link_data = self.data.get(switch_name)
        if link_data is not None:
            return [link_data]  # Restituisce i dati del link come lista
        else:
            print(f"Nessun dato disponibile per lo switch {switch_name}")
            return []  # Restituisce una lista vuota se non ci sono dati disponibili

    def add_traffic_data(self, link):
        # Aggiunge un oggetto Link ai dati di traffico
        self.traffic_data.append(link)

    def get_traffic_data(self, switch_info):
        if not self.traffic_data:
            return None

        filtered_traffic_data = self.filter_traffic_data(self.traffic_data, switch_info)
        return filtered_traffic_data

    def filter_traffic_data(self, traffic_data, switch_info):
        filtered_data = [link for link in traffic_data if self.filter_criteria(link, switch_info)]
        return filtered_data

    def filter_criteria(self, link, switch_info):
        return link.switch_name == switch_info.name
