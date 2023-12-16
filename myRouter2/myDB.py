import json
import psycopg2
from psycopg2 import sql

#paramentri connessione
parametri_connessione = {
        'host': 'localhost',
        'user': 'il_tuo_utente',
        'password': 'la_tua_password',
        'database': 'postgres',
        'port': 5432
    }

# Variabile globale per la connessione al database
db_connection = None

def DB_connection():
    global db_connection
    try:
        db_connection = psycopg2.connect(**parametri_connessione)
        print("Connessione al database riuscita!")

    except psycopg2.OperationalError as e:
        print(f"Errore operativo durante la connessione al database: {e}")
    except psycopg2.DatabaseError as e:
        print(f"Errore del database durante la connessione al database: {e}")
    except Exception as e:
        print(f"Errore generico durante la connessione al database: {e}")
    return db_connection

def create_database_if_not_exists(db_name):
    connection = DB_connection()

    try:
        with connection.cursor() as cursor:
            # Query SQL per verificare se il database esiste già
            check_database_query = sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(sql.Placeholder())
            cursor.execute(check_database_query, (db_name,))
            database_exists = cursor.fetchone()
            print(f"Il database esiste")

            # Se il database non esiste, lo creiamo
            if not database_exists:
                create_database_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
                cursor.execute(create_database_query)
                print(f"Database '{db_name}' creato con successo.")

    except psycopg2.Error as e:
        print(f"Errore durante la creazione del database: {e}")

    finally:
        if connection:
            connection.close()



def create_table_if_not_exists():

    global connection

    try:
        # Connessione al database
        connection = DB_connection()

        # Creazione dell'oggetto cursore
        cursor = connection.cursor()

        # Verifica se la tabella esiste già
        table_name = input("Inserisci il nome della tabella ...")
        table_exists_query = sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);")
        cursor.execute(table_exists_query, [table_name])
        table_exists = cursor.fetchone()[0]
        print(f"La tabella esiste")

        # Se la tabella non esiste, la creiamo
        if not table_exists:

         #Se columns_definition non è specificato, richiedilo da tastiera
         columns_definition = input("Inserisci la definizione delle colonne (es. col1 INT, col2 VARCHAR(255), ...): ")

         create_table_query = sql.SQL("CREATE TABLE {} ({})").format(
             sql.Identifier(table_name),
             sql.SQL(columns_definition)
         )
         cursor.execute(create_table_query)
         print(f"Tabella '{table_name}' creata con successo.")

        # Commit delle modifiche
         connection.commit()

    except psycopg2.Error as e:
        print(f"Errore durante l'interazione con il database: {e}")

    finally:
        # Chiusura della connessione
        if connection:
            connection.close()



def insert_data_into_table(table_name, data):
    global connection
    try:
        # Connessione al database
        connection = DB_connection()

        # Creazione dell'oggetto cursore
        cursor = connection.cursor()

        # Inserimento dei dati nella tabella
        insert_data_query = sql.SQL("INSERT INTO {} VALUES (%s);").format(sql.Identifier(table_name))

        # Converti la stringa JSON in un oggetto Python
        data_json = json.dumps(data)

        # Passa i valori come parte di una tupla
        cursor.execute(insert_data_query, (data_json,))

        print(f"Dati inseriti con successo nella tabella {table_name}.")

        # Commit delle modifiche
        connection.commit()

    except psycopg2.Error as e:
        print(f"Errore durante l'interazione con il database: {e}")
    finally:
        # Chiusura della connessione
        if connection:
            connection.close()