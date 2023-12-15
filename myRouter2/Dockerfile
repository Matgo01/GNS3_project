FROM debian:bullseye

# Aggiorna l'indice dei pacchetti e installa Python e pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Aggiorna pip
RUN pip3 install --upgrade pip

# Installa le dipendenze del tuo script
RUN pip3 install requests Flask

# Altre dipendenze specificate nel tuo script Python
RUN pip3 install gevent

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia tutti i file Python necessari nella directory di lavoro

COPY myDB.py /app/Router2.py

COPY myRouter2.py /app/myRouter2.py

#espongo la porta di ascolto
EXPOSE 5020


# Imposta i permessi di esecuzione per gli script Python
RUN chmod +x /app/myRouter2.py


# Comando di avvio dell'applicazione
ENTRYPOINT ["python3", "/app/myRouter2.py"]
