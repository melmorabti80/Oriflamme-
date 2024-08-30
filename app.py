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
            FOREIGN KEY (SeasonID) REFERENCES seasons(SeasonID)
        )
        """)
        
        # Vérifier si les colonnes DatePlayed et SeasonID existent, sinon les ajouter
        cursor.execute("SHOW COLUMNS FROM games LIKE 'DatePlayed'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE games ADD COLUMN DatePlayed DATE")
        
        cursor.execute("SHOW COLUMNS FROM games LIKE 'SeasonID'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE games ADD COLUMN SeasonID INT")
            cursor.execute("ALTER TABLE games ADD FOREIGN KEY (SeasonID) REFERENCES seasons(SeasonID)")

        # Vérifier et créer la table des parties archivées
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS archived_games (
            GameID INT AUTO_INCREMENT PRIMARY KEY,
            Winning_Team VARCHAR(255),
            Losing_Team VARCHAR(255),
            DatePlayed DATE,
            SeasonID INT,
            FOREIGN KEY (SeasonID) REFERENCES seasons(SeasonID)
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

# Fonction pour supprimer une partie
def delete_game(game_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "DELETE FROM games WHERE GameID = %s"
            cursor.execute(query, (game_id,))
            connection.commit()
        except Error as e:
            st.error(f"Erreur lors de la suppression de la partie: {e}")
        finally:
            cursor.close()
            connection.close()

# Fonction pour charger les données depuis la base de données
def load_data(season_id=None):
    connection = create_connection()
    df = pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed'])
    if connection:
        cursor = connection.cursor()
        try:
            if season_id:
                query = "SELECT GameID, Winning_Team, Losing_Team, DatePlayed FROM games WHERE SeasonID = %s"
                cursor.execute(query, (season_id,))
            else:
                query = "SELECT GameID, Winning_Team, Losing_Team, DatePlayed FROM games"
                cursor.execute(query)
            records = cursor.fetchall()
            df = pd.DataFrame(records, columns=['GameID', 'Winning_Team', 'Losing_Team', 'DatePlayed'])
        except Error as e:
            st.error(f"Erreur lors du chargement des données: {e}")
        finally:
            cursor.close()
            connection.close()
    return df

# Fonction pour calculer les scores et les coéquipiers
def calculate_scores(df):
    players_stats = {player: {'Games_Won': 0, 'Games_Played': 0} for player in PLAYERS}
    teammates_wins = {player: {} for player in PLAYERS}
    teammates_losses = {player: {} for player in PLAYERS}

    for _, row in df.iterrows():
        winning_team = row['Winning_Team'].split(', ')
        losing_team = row['Losing_Team'].split(', ')

        for player in winning_team:
            players_stats[player]['Games_Won'] += 1
            players_stats[player]['Games_Played'] += 1
            teammate = winning_team[1] if winning_team[0] == player else winning_team[0]
            if teammate not in teammates_wins[player]:
                teammates_wins[player][teammate] = 0
            teammates_wins[player][teammate] += 1

        for player in losing_team:
            players_stats[player]['Games_Played'] += 1
            teammate = losing_team[1] if losing_team[0] == player else losing_team[0]
            if teammate not in teammates_losses[player]:
                teammates_losses[player][teammate] = 0
            teammates_losses[player][teammate] += 1

    # Trouver le coéquipier avec lequel chaque joueur gagne/perd le plus
    for player in PLAYERS:
        players_stats[player]['Best_Teammate_Wins'] = max(teammates_wins[player], key=teammates_wins[player].get, default='N/A')
        players_stats[player]['Best_Teammate_Wins_Count'] = teammates_wins[player].get(players_stats[player]['Best_Teammate_Wins'], 0)
        players_stats[player]['Best_Teammate_Losses'] = max(teammates_losses[player], key=teammates_losses[player].get, default='N/A')
        players_stats[player]['Best_Teammate_Losses_Count'] = teammates_losses[player].get(players_stats[player]['Best_Teammate_Losses'], 0)

    scores = pd.DataFrame([{'Player': player, 
                            'Games_Won': stats['Games_Won'], 
                            'Games_Played': stats['Games_Played'], 
                            'Score': round((stats['Games_Won'] / stats['Games_Played']) * 100, 2) if stats['Games_Played'] > 0 else 0,
                            'Best_Teammate_Wins': stats['Best_Teammate_Wins'],
                            'Best_Teammate_Wins_Count': stats['Best_Teammate_Wins_Count'],
                            'Best_Teammate_Losses': stats['Best_Teammate_Losses'],
                            'Best_Teammate_Losses_Count': stats['Best_Teammate_Losses_Count']}
                           for player, stats in players_stats.items()])
    
    return scores

# Fonction pour archiver une saison
def archive_season():
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
                connection.commit()
        
        except Error as e:
            st.error(f"Erreur lors de l'archivage de la saison: {e}")
        finally:
            cursor.close()
            connection.close()

# Fonction pour créer une nouvelle saison
def create_new_season():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Trouver le numéro de la prochaine saison
            cursor.execute("SELECT COUNT(*) FROM seasons")
            count = cursor.fetchone()[0]
            new_season_name = f"Saison {count + 1}"
            
            # Créer la nouvelle saison
            cursor.execute("INSERT INTO seasons (SeasonName, StartDate) VALUES (%s, %s)", (new_season_name, datetime.now().date()))
            connection.commit()
        
        except Error as e:
            st.error(f"Erreur lors de la création de la nouvelle saison: {e}")
        finally:
            cursor.close()
            connection.close()

# Créer la base de données si elle n'existe pas
create_database()

# Vérifier et créer les tables si nécessaire
verify_and_create_tables()

# Charger les données de la saison actuelle
df = load_data()

# Interface utilisateur
st.title('Oriflamme Score Tracker')

st.header('Ajouter une nouvelle partie')
winning_team = st.multiselect('Sélectionnez les joueurs de l\'équipe gagnante', PLAYERS, max_selections=2)
losing_team = st.multiselect('Sélectionnez les joueurs de l\'équipe perdante', PLAYERS, max_selections=2)

if st.button('Ajouter Partie'):
    if len(winning_team) == 2 and len(losing_team) == 2:
        add_game(winning_team, losing_team)
        st.success('Partie ajoutée avec succès!')
    else:
        st.error('Chaque équipe doit avoir exactement 2 joueurs.')
    df = load_data()  # Recharger les données après l'ajout

# Afficher les parties enregistrées
st.header('Parties enregistrées')
if not df.empty:
    st.table(df)
else:
    st.write("Aucune partie enregistrée.")

# Suppression d'une partie
st.header('Supprimer une partie')
if not df.empty:
    game_id_to_delete = st.number_input('Entrer l\'ID de la partie à supprimer', min_value=1, max_value=df['GameID'].max(), step=1)

    if st.button('Supprimer Partie'):
        delete_game(game_id_to_delete)
        st.success(f'Partie ID {game_id_to_delete} supprimée avec succès!')
        df = load_data()  # Recharger les données après la suppression
else:
    st.write("Aucune partie à supprimer.")

# Archiver la saison en cours et créer une nouvelle saison
if st.button('Archiver la Saison et Créer une Nouvelle Saison'):
    archive_season()
    create_new_season()
    st.success('Saison archivée et nouvelle saison créée!')
    df = load_data()  # Recharger les données pour la nouvelle saison

# Afficher les scores actuels
scores_df = calculate_scores(df)
scores_df = scores_df.sort_values(by='Score', ascending=False)
st.header('Scores actuels')
st.table(scores_df)

# Sélectionner une saison pour voir les parties archivées
st.header('Voir les Saisons Archivées')
connection = create_connection()
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

season_options = {season[1]: season[0] for season in seasons}
selected_season_name = st.selectbox('Sélectionnez une Saison', list(season_options.keys()))

if selected_season_name:
    selected_season_id = season_options[selected_season_name]
    archived_df = load_data(selected_season_id)
    st.header(f'Parties de {selected_season_name}')
    if not archived_df.empty:
        st.table(archived_df)
    else:
        st.write("Aucune partie enregistrée pour cette saison.")
