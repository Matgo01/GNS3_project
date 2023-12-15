#!/usr/bin/env python3
import os
import time
import paho.mqtt.client as mqtt
#from mySDNswitch2.MySwitch import MySwitch

#il dispositivo utilizza il protocollo di cominicazione mqtt

class IoTDeviceNumber7:

    #def __init__(self,ip,mac,switch):
        #self.ip=ip
        #self.mac=mac
        #self.switch=switch

    def __init__(self,ip,mac):
        self.ip=ip
        self.mac=mac
        self.client = mqtt.Client()
        # Configurazione TLS
        #self.client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt")


    #def connect(self):
           #apertura connessione allo switch
         #self.conn=self.switch.conncet(self.ip,self.mac)

    #def send(self,data):
          #invio dati allo switch
         #self.conn.send(data)

    def disconnect(self):
        #chiudo la connesione
        self.client.disconnect()
    def connect(self):
        self.client.connect("127.0.0.1", 5020)
        print(f"connesso al router ")

    def send_data(self,data):
        #invio dati allo switch tramite mqtt
        message = f"MQTT_MESSAGE\n{data}"
        self.client.publish("meteo", message)
        print(f"dati pubblicati")
        #client.disconnect()

    def check_mqtt_status(self):
        #controlla lo stato del server mqtt

        try:
            self.client.connect("127.0.0.1", 5020)
            return True
        except Exception as e:
            return False

    def subscribe_to_topic(self, topic):
        # Funzione per iscriversi a un topic MQTT
        subscribe_message = f"MQTT_SUBSCRIBE\n{topic}"
        self.client.subscribe(subscribe_message)
        print(f"Iscritto al topic: {subscribe_message}")


    def on_message(client, message):
        # Funzione di gestione dei messaggi MQTT ricevuti
        payload_bytes = message.payload  # Il payload è già in formato bytes
        payload_str = payload_bytes.decode("utf-8")  # Decodifica da binario a stringa

        print(f"Ricevuto messaggio sul topic {message.topic}: {payload_str}")


def main():
    #creazione switch sdn
    #switch = MySwitch("mySDNSwitch","127.0.0.1",90)
    #switch.connect()

    #creazione dispositivo iot
    #device= IoTDeviceNumber3('192.168.3.1', 'aa:bb:cc:dd:ee:ff', switch)
    device = IoTDeviceNumber7('192.168.3.1', 'aa:bb:cc:dd:ee:ff')
    device.connect()
    device.subscribe_to_topic('meteo')
    #Indico il path
    path = os.path.join('JSON1.json')

    #apertura e lettura file json
    with open(path) as f:
        data = f.read()


    #ciclo di controllo sullo stato del server mqtt
    while True:
        if device.check_mqtt_status():
            #se il server mqtt è attivo, continua a funzionare
            #invio dati
            device.send_data(data)
            time.sleep(10)
            continue
        else:
            #se il server mqtt non è attivo, si spegne
            device.disconnect()
            break

if __name__== '__main__':
    main()
