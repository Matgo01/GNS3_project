import threading
from MySwitch import MySwitch
from Sensor import Sensor

class SDNController:
    def __init__(self,sdn_address,sdn_port):
        #dizionario per mantenere riferiementi a switch e sensori
        self.cache = {}
        self.switches = {}
        self.sensors = {}
        #soglia di conegestione del traffico
        self.THRESHOLD = 80
        self.sdn_address = sdn_address
        self.sdn_port = sdn_port

    def add_switch(self, switch):
        #aggiungo uno switch al dizionario
        self.switches[switch.name] = switch

    def remove_switch(self, switch_name):
        #rimuovo uno switch dal dizionario
        if switch_name in self.switches:
            del self.switches[switch_name]

    def add_sensor(self, sensor):
        #aggiungo un sensore al dizionario
        self.sensors[sensor.name] = sensor

    def remove_sensor(self, sensor_name):
        #rimuovo un sensore dal dizionario
        if sensor_name in self.sensors:
            del self.sensors[sensor_name]

    def monitor_network(self):
        #lista per mantenere i riferimenti ai thread
        threads = []
        #monitoro gli switch
        for switch in self.switches.values():
            thread = threading.Thread(target=self.monitor_switch, args=(switch,))
            threads.append(thread)
            thread.start()
        #monitoro i sensori
        for sensor in self.sensors.values():
            thread = threading.Thread(target=self.monitor_sensor, args=(sensor,))
            threads.append(thread)
            thread.start()
        #raccolgo i dati dai sensori
        for sensor in self.sensors.values():
            sensor.collect_data()
        #attendo il completamento di tutti i thread
        for thread in threads:
            thread.join()

    def monitor_switch(self, switch):
        #ottengo informazioni sullo switch e analizzo
        switch_info = switch.get_info()
        self.analyze_switch(switch, switch_info)

    def monitor_sensor(self, sensor):
        #ottengo dati dal sensore e analizzo
        sensor_data = sensor.get_data()
        self.analyze_sensor_data(sensor_data, None)

    def analyze_switch(self, switch, switch_info):
        #analizzo i dati dei sensori per ciascuno switch
        for sensor_name, sensor in self.sensors.items():
            sensor_data = sensor.get_data(switch)
            self.analyze_sensor_data(sensor_data, switch_info)

    def analyze_sensor_data(self, sensor_data, switch_info):
        # Analizzo i dati dei sensori per la congestione del traffico
        traffic_data = sensor_data.get_traffic_data(switch_info)

        # Aggiunta del controllo per verificare se traffic_data è iterable
        if not hasattr(traffic_data, '__iter__'):
            self.log_error("Dati del traffico non sono iterabili.")
            return

        for link in traffic_data:
            if link.bandwidth_usage > self.THRESHOLD:
                self.send_notification(f"congestione rilevata sul link {link.name}")

            if link.bandwidth_usage > self.THRESHOLD * 2:
                self.reduce_bandwidth(link, self.THRESHOLD)
            else:
                self.rebalance_traffic(link)

            if link.bandwidth_usage > self.THRESHOLD * 2:
                self.send_emergency_notification(f"congestione grave rilevata sul link {link.name}")

            if link.bandwidth_usage < 0:
                self.log_error(f"i dati del sensore per il link {link.name} non sono validi")

    def send_notification(self, message):
        #mando una notifica
        print("Notification:", message)

    def send_emergency_notification(self, message):
        #mando una notifica di emergenza
        print("Emergency Notification:", message)

    def reduce_bandwidth(self, link, threshold):
        #riduco l'utilizzo della banda di un link
        link.set_bandwidth(threshold)
        print(f"Reduced bandwidth for link {link.name} to {threshold}")

    def rebalance_traffic(self, link):
        #ricolloco il traffico su un nuovo link disponibile
        new_link = self.find_available_link()
        if new_link:
            self.add_flow(self.get_switch(link), f"in_port={link.name}", f"out_port={new_link.name}", f"actions=output:{new_link.name}")
            print(f"Rebalanced traffic from link {link.name} to {new_link.name}")
        else:
            print(f"No available link for rebalancing traffic from link {link.name}")

    def log_error(self, message):
        #registro un errore nel file log
        with open("error_log.txt", "a") as log_file:
            log_file.write("Error: " + message + "\n")
        print("Error logged:", message)

    def find_available_link(self):
        #trovo un link disposnibile
        available_links = self.get_available_links()
        if available_links:
            return available_links[0]
        else:
            return None

    def get_available_links(self):
        #ottengo tutti i link disponibili tea gli switch
        available_links = []
        for switch in self.switches.values():
            for link in switch.links:
                if link.is_available():
                    available_links.append(link)
        return available_links

    def get_switch(self, link):
        #trovo lo switch associato al link
        for switch in self.switches.values():
            if link in switch.links:
                return switch

    def add_flow(self, switch, in_port, out_port, actions):
        #aggiungo un flusso allo switch
        switch.add_flow(in_port, out_port, actions)

    def get_flows(self, switch):
        #ottengo i flussi dallo switch
        return switch.get_flows()

    def configure_switch(self, switch, link):
        #configura lo switch in risposta alla congestione
        switch.set_link_bandwidth(link.name, self.THRESHOLD)
        switch.send_message(f"la larghezza di banda del link {link.name} è stata ridotta a {self.THRESHOLD}")
        #invia un messaggio a tutti i sensori associati
        for sensor_name, sensor in self.sensors.items():
            sensor.send_message(f"la larghezza di banda del link {link.name} è stata ridotta a {self.THRESHOLD}")
        #attendo applicazioner della configurazione da parte dello switch
        switch.wait_for_config_apply()
        #ottengo i dati del traffico aggiornati
        traffic_data = switch.get_traffic_data()
        #trovo link alternativi disponibili
        alternative_links = []
        for alt_link in traffic_data:
            if alt_link.name != link.name:
                alternative_links.append(alt_link)
        #ricolloco i flussi su link alternativi
        for flow in traffic_data:
            if flow.link == link.name:
                for alt_link in alternative_links:
                    if alt_link.bandwidth_usage < self.THRESHOLD:
                        switch.add_flow(flow.src_mac, flow.dst_mac, alt_link.name)

    def cache_sensor_data(self):
        #caching dai dati dai sensori
        for sensor_name, sensor in self.sensors.items():
            sensor_data = sensor.get_data()
            self.cache[sensor_name] = sensor_data

    def prioritize_traffic(self, link,switch):
        #ottengo i flussi di traffico e ordino per priorità
        flows = self.get_flows(switch=switch)
        flows.sort(key=lambda flow: flow.priority)
        #configuro lo switch per prioritare i flussi
        for flow in flows:
            self.add_flow(link, flow.in_port, flow.out_port, flow.actions)

def main():
    #inizializzo il controller SDN, uno switch e un sensore
    controller = SDNController('localhost', 90)
    switch = MySwitch('MySDNswitch','Bridge',controller.sdn_address,controller.sdn_port)
    switch.connect()
    controller.add_switch(switch)
    controller.add_flow(switch, 'in_port=tap1', 'out_port=tap2', 'actions=output:tap2')
    sensor = Sensor('sensore1', 'traffic', 'openflow')
    controller.add_sensor(sensor)

    try:
        #monitora costantemente la rete SDN
        while True:
            controller.monitor_network()
            flows = controller.get_flows(switch)
            switch_info = switch.get_info()
            sensor_data = sensor.get_data('MySDNswitch')
            if not hasattr(sensor_data, '__iter__'):
                controller.log_error("Dati del sensore non sono iterabili.")
                continue
            for link in controller.analyze_sensor_data(sensor_data,switch_info):
                if link.bandwidth_usage > controller.THRESHOLD:
                    #configuro lo switch in caso di congestione
                    controller.configure_switch(switch, link)
    except KeyboardInterrupt:
        print("Ctrl+C rilevato. Uscita dal programma.")

if __name__ == '__main__':
    main()
