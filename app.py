import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Informations de connexion à la base de données MySQL
DB_HOST = 'oriflamme.clawkwcigwq6.eu-north-1.rds.amazonaws.com'
DB_NAME = 'oriflamme'
DB_USER = 'admin'
DB_PASSWORD = 'Mohamed80'

# Liste des joueurs
PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

# Fonction pour se connecter à la base de données MySQL et vérifier/créer la table
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            GameID INT AUTO_INCREMENT PRIMARY KEY,
            Winning_Team VARCHAR(255),
            Losing_Team VARCHAR(255)
        )
        """)
        connection.commit()
        cursor.close()
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
    return connection

# Fonction pour ajouter une nouvelle partie
def add_game(winning_team, losing_team):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = """
        INSERT INTO games (Winning_Team, Losing_Team)
        VALUES (%s, %s)
        """
        winning_team_str = ', '.join(winning_team)
        losing_team_str = ', '.join(losing_team)
        cursor.execute(query, (winning_team_str, losing_team_str))
        connection.commit()
        cursor.close()
        connection.close()

# Fonction pour supprimer une partie
def delete_game(game_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "DELETE FROM games WHERE GameID = %s"
        cursor.execute(query, (game_id,))
        connection.commit()
        cursor.close()
        connection.close()

# Fonction pour charger les données depuis la base de données
def load_data():
    connection = create_connection()
    df = pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team'])
    if connection:
        cursor = connection.cursor()
        query = "SELECT GameID, Winning_Team, Losing_Team FROM games"
        cursor.execute(query)
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['GameID', 'Winning_Team', 'Losing_Team'])
        cursor.close()
        connection.close()
    return df

# Fonction pour calculer les scores
def calculate_scores(df):
    players_stats = {player: {'Games_Won': 0, 'Games_Played': 0} for player in PLAYERS}

    for _, row in df.iterrows():
        winning_team = row['Winning_Team'].split(', ')
        losing_team = row['Losing_Team'].split(', ')

        for player in winning_team:
            players_stats[player]['Games_Won'] += 1
            players_stats[player]['Games_Played'] += 1

        for player in losing_team:
            players_stats[player]['Games_Played'] += 1

    scores = pd.DataFrame([{'Player': player, 
                            'Games_Won': stats['Games_Won'], 
                            'Games_Played': stats['Games_Played'], 
                            'Score': round((stats['Games_Won'] / stats['Games_Played']) * 100, 2) if stats['Games_Played'] > 0 else 0}
                           for player, stats in players_stats.items()])
    
    return scores

# Charger les données
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

# Afficher les scores actuels
scores_df = calculate_scores(df)
scores_df = scores_df.sort_values(by='Score', ascending=False)
st.header('Scores actuels')
st.table(scores_df)
