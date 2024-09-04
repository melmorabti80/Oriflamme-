import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Informations de connexion à la base de données MySQL
DB_HOST = 'oriflamme.clawkwcigwq6.eu-north-1.rds.amazonaws.com'
DB_NAME = 'oriflamme'
DB_USER = 'admin'
DB_PASSWORD = 'Mohamed80'

# Liste des joueurs
PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

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
        
        # Vérifier et créer la table des saisons
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            SeasonID INT AUTO_INCREMENT PRIMARY KEY,
            SeasonName VARCHAR(255),
            StartDate DATE
        )
        """)
        
        # Vérifier et créer la table des parties actuelles
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
        
        # Vérifier et créer la table des parties archivées
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

# Fonction pour ajouter une nouvelle partie
def add_game(winning_team, losing_team):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Récupérer la saison actuelle
            cursor.execute("SELECT SeasonID FROM seasons ORDER BY SeasonID DESC LIMIT 1")
            current_season = cursor.fetchone()
            
            if current_season:
                season_id = current_season[0]
                query = """
                INSERT INTO games (Winning_Team, Losing_Team, DatePlayed, SeasonID)
                VALUES (%s, %s, %s, %s)
                """
                winning_team_str = ', '.join(winning_team)
                losing_team_str = ', '.join(losing_team)
                cursor.execute(query, (winning_team_str, losing_team_str, datetime.now().date(), season_id))
                connection.commit()
            
        except Error as e:
            st.error(f"Erreur lors de l'ajout de la partie: {e}")
        finally:
            cursor.close()
            connection.close()

# Fonction pour archiver la saison actuelle et démarrer une nouvelle saison
def archive_and_create_new_season():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Récupérer la saison actuelle
            cursor.execute("SELECT SeasonID FROM seasons ORDER BY SeasonID DESC LIMIT 1")
            current_season = cursor.fetchone()
            
            if current_season:
                season_id = current_season[0]
                
                # Archiver les parties de la saison actuelle
                cursor.execute("""
                INSERT INTO archived_games (Winning_Team, Losing_Team, DatePlayed, SeasonID)
                SELECT Winning_Team, Losing_Team, DatePlayed, SeasonID FROM games WHERE SeasonID = %s
                """, (season_id,))
                
                # Supprimer les parties archivées de la table actuelle
                cursor.execute("DELETE FROM games WHERE SeasonID = %s", (season_id,))
                
                # Créer la nouvelle saison
                cursor.execute("SELECT COUNT(*) FROM seasons")
                count = cursor.fetchone()[0]
                new_season_name = f"Saison {count + 1}"
                cursor.execute("INSERT INTO seasons (SeasonName, StartDate) VALUES (%s, %s)", (new_season_name, datetime.now().date()))
                
                connection.commit()
        
        except Error as e:
            st.error(f"Erreur lors de l'archivage de la saison ou la création de la nouvelle saison: {e}")
        finally:
            cursor.close()
            connection.close()

# Fonction pour charger les données depuis la base de données
def load_data(season_id=None):
    connection = create_connection()
    df = pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed', 'SeasonName'])
    if connection:
        cursor = connection.cursor()
        try:
            query = """
            SELECT g.GameID, g.Winning_Team, g.Losing_Team, g.DatePlayed, s.SeasonName
            FROM games g
            JOIN seasons s ON g.SeasonID = s.SeasonID
            """
            if season_id:
                query += " WHERE g.SeasonID = %s"
                cursor.execute(query, (season_id,))
            else:
                cursor.execute(query)
            
            records = cursor.fetchall()
            df = pd.DataFrame(records, columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed', 'SeasonName'])
        except Error as e:
            st.error(f"Erreur lors du chargement des données: {e}")
        finally:
            cursor.close()
            connection.close()
    return df

# Fonction pour vérifier s'il existe une saison active et en créer une si nécessaire
def ensure_current_season():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM seasons")
            count = cursor.fetchone()[0]
            if count == 0:
                # Créer la première saison si aucune n'existe
                cursor.execute("INSERT INTO seasons (SeasonName, StartDate) VALUES (%s, %s)", ("Saison 1", datetime.now().date()))
                connection.commit()
        except Error as e:
            st.error(f"Erreur lors de la vérification/création de la saison actuelle: {e}")
        finally:
            cursor.close()
            connection.close()

# Créer la base de données si elle n'existe pas
create_database()

# Vérifier et créer les tables si nécessaire
verify_and_create_tables()

# Assurer qu'une saison actuelle existe
ensure_current_season()

# Interface utilisateur avec menu latéral
st.sidebar.title("Menu de Navigation")
menu = st.sidebar.radio("Choisissez une option", ["Saison en cours", "Saisons archivées", "Suppression des données"])

if menu == "Saison en cours":
    st.title('Saison en cours')
    
    # Charger les données de la saison actuelle
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT SeasonID FROM seasons ORDER BY SeasonID DESC LIMIT 1")
    current_season = cursor.fetchone()
    current_season_id = current_season[0]
    
    df = load_data(current_season_id)
    
    st.header('Ajouter une nouvelle partie')
    winning_team = st.multiselect('Sélectionnez les joueurs de l\'équipe gagnante', PLAYERS, max_selections=2)
    losing_team = st.multiselect('Sélectionnez les joueurs de l\'équipe perdante', PLAYERS, max_selections=2)

    if st.button('Ajouter Partie'):
        if len(winning_team) == 2 and len(losing_team) == 2:
            add_game(winning_team, losing_team)
            st.success('Partie ajoutée avec succès!')
            df = load_data(current_season_id)  # Recharger les données après l'ajout
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')

    # Afficher les parties enregistrées de la saison actuelle
    st.header('Parties enregistrées de la saison actuelle')
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")

    # Archiver la saison en cours et démarrer une nouvelle saison
    if st.button('Archiver la saison et débuter une nouvelle saison'):
        archive_and_create_new_season()
        st.success('Saison archivée et nouvelle saison créée avec succès!')
        df = load_data(current_season_id)

elif menu == "Saisons archivées":
    st.title('Saisons archivées')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT SeasonID, SeasonName FROM seasons WHERE SeasonID IN (SELECT DISTINCT SeasonID FROM archived_games)")
            archived_seasons = cursor.fetchall()
        except Error as e:
            st.error(f"Erreur lors du chargement des saisons archivées: {e}")
        finally:
            cursor.close()
            connection.close()

    if archived_seasons:
        selected_season_name = st.selectbox('Sélectionnez une Saison pour voir les détails', [season[1] for season in archived_seasons])
        selected_season_id = next(season[0] for season in archived_seasons if season[1] == selected_season_name)
        df = load_data(selected_season_id)

        if not df.empty:
            st.table(df)
            # Vous pouvez également afficher le classement ici si nécessaire
        else:
            st.write("Aucune partie enregistrée pour cette saison.")
    else:
        st.write("Aucune saison archivée disponible.")

elif menu == "Suppression des données":
    st.title('Suppression des données')

    connection = create_connection()
    seasons = []
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT SeasonID, SeasonName FROM seasons")
            seasons = cursor.fetchall()
        except Error as e:
            st.error(f"Erreur lors du chargement des saisons: {e}")
        finally:
            cursor.close()
            connection.close()

    season_options = {'Toutes les saisons': 'Toutes les saisons', 'Toutes les parties': 'Toutes les parties'}
    season_options.update({season[1]: season[0] for season in seasons})
    selected_option = st.selectbox('Sélectionnez une option pour supprimer', list(season_options.keys()))

    if st.button('Supprimer'):
        option_value = season_options[selected_option]
        delete_season_or_games(option_value)
        st.success(f'{selected_option} supprimé(e) avec succès!')
