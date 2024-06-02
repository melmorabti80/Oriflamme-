import streamlit as st
import pandas as pd
import os

# Chemin du fichier CSV
FILE_PATH = "oriflamme_games.csv"

# Liste des joueurs
PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

# Fonction pour charger le fichier CSV
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team'])
    else:
        return pd.DataFrame(columns=['GameID', 'Winning_Team', 'Losing_Team'])

# Charger les données
df = load_data(FILE_PATH)

# Fonction pour ajouter une nouvelle partie
def add_game(winning_team, losing_team):
    global df
    new_game = pd.DataFrame({'GameID': [len(df) + 1], 
                             'Winning_Team': [', '.join(winning_team)], 
                             'Losing_Team': [', '.join(losing_team)]})
    df = pd.concat([df, new_game], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

# Fonction pour supprimer une partie
def delete_game(game_id):
    global df
    df = df[df['GameID'] != game_id]
    df.to_csv(FILE_PATH, index=False)

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

# Afficher les parties enregistrées
st.header('Parties enregistrées')
if not df.empty:
    st.table(df)
else:
    st.write("Aucune partie enregistrée.")

# Suppression d'une partie
st.header('Supprimer une partie')
if not df.empty:
    game_id_to_delete = st.number_input('Entrer l\'ID de la partie à supprimer', min_value=1, max_value=len(df), step=1)

    if st.button('Supprimer Partie'):
        delete_game(game_id_to_delete)
        st.success(f'Partie ID {game_id_to_delete} supprimée avec succès!')
else:
    st.write("Aucune partie à supprimer.")

# Calculer les scores
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

# Afficher les scores actuels
scores_df = calculate_scores(df)
scores_df = scores_df.sort_values(by='Score', ascending=False)
st.header('Scores actuels')
st.table(scores_df)

# Sauvegarder les scores dans un fichier CSV séparé (optionnel)
scores_df.to_csv('oriflamme_scores.csv', index=False)
