import streamlit as st
import mysql.connector
from mysql.connector import Error

# Informations de connexion à la base de données MySQL
DB_HOST = 'oriflamme.clawkwcigwq6.eu-north-1.rds.amazonaws.com'
DB_NAME = 'oriflamme'
DB_USER = 'admin'
DB_PASSWORD = 'Mohamed80'

def test_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            st.success(f"Connecté au serveur MySQL version {db_info}")
            connection.close()
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")

test_connection()
