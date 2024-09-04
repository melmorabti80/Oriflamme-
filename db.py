import mysql.connector
from mysql.connector import Error
import streamlit as st

DB_HOST = 'oriflamme.clawkwcigwq6.eu-north-1.rds.amazonaws.com'
DB_NAME = 'oriflamme'
DB_USER = 'admin'
DB_PASSWORD = 'Mohamed80'

# Fonction pour créer la base de données si elle n'existe pas
def create_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")

# Fonction pour se connecter à la base de données MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Fonction pour vérifier et créer les tables si elles n'existent pas
def verify_and_create_tables():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                SeasonID INT AUTO_INCREMENT PRIMARY KEY,
                SeasonName VARCHAR(255),
                StartDate DATE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                GameID INT AUTO_INCREMENT PRIMARY KEY,
                Winning_Team VARCHAR(255),
                Losing_Team VARCHAR(255),
                DatePlayed DATE,
                SeasonID INT,
                FOREIGN KEY (SeasonID) REFERENCES seasons(SeasonID) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archived_games (
                GameID INT AUTO_INCREMENT PRIMARY KEY,
                Winning_Team VARCHAR(255),
                Losing_Team VARCHAR(255),
                DatePlayed DATE,
                SeasonID INT,
                FOREIGN KEY (SeasonID) REFERENCES seasons(SeasonID) ON DELETE CASCADE
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

# Fonction pour vérifier s'il existe une saison active et en créer une si nécessaire
def ensure_current_season():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM seasons")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("INSERT INTO seasons (SeasonName, StartDate) VALUES (%s, %s)", ("Saison 1", datetime.now().date()))
            connection.commit()
        cursor.close()
        connection.close()

# Fonction pour charger les parties d'une saison
def load_data(season_id=None, archived=False):
    connection = create_connection()
    df = pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed', 'SeasonName'])
    if connection:
        cursor = connection.cursor()
        table = "archived_games" if archived else "games"
        query = f"""
            SELECT g.GameID, g.Winning_Team, g.Losing_Team, g.DatePlayed, s.SeasonName
            FROM {table} g
            JOIN seasons s ON g.SeasonID = s.SeasonID
        """
        if season_id:
            query += " WHERE g.SeasonID = %s"
            cursor.execute(query, (season_id,))
        else:
            cursor.execute(query)
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed', 'SeasonName'])
        cursor.close()
        connection.close()
    return df

# Autres fonctions (add_game, archive_and_create_new_season) peuvent être ajoutées ici

