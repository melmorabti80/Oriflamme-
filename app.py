import streamlit as st
import pandas as pd
import os

# Chemin du fichier CSV
FILE_PATH = "oriflamme_scores.csv"

# Liste des joueurs
PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

# Fonction pour charger le fichier CSV
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['Player', 'Games_Won', 'Games_Played'])
    else:
        return pd.DataFrame(columns=['Player', 'Games_Won', 'Games_Played'])

# Charger les données
df = load_data(FILE_PATH)

# Fonction pour mettre à jour les scores
def update_scores(winning_team, losing_team):
    global df
    for player in winning_team:
        if player in df['Player'].values:
            df.loc[df['Player'] == player, 'Games_Won'] += 1
            df.loc[df['Player'] == player, 'Games_Played'] += 1
        else:
            new_row = pd.DataFrame({'Player': [player], 'Games_Won': [1], 'Games_Played': [1]})
            df = pd.concat([df, new_row], ignore_index=True)

    for player in losing_team:
        if player in df['Player'].values:
            df.loc[df['Player'] == player, 'Games_Played'] += 1
        else:
            new_row = pd.DataFrame({'Player': [player], 'Games_Won': [0], 'Games_Played': [1]})
            df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(FILE_PATH, index=False)

# Calculer le score en pourcentage
def calculate_score(df):
    df['Score'] = (df['Games_Won'] / df['Games_Played'] * 100).round(2)
    return df

# Interface utilisateur
st.title('Oriflamme Score Tracker')

st.header('Ajouter une nouvelle partie')
winning_team = st.multiselect('Sélectionnez les joueurs de l\'équipe gagnante', PLAYERS, max_selections=2)
losing_team = st.multiselect('Sélectionnez les joueurs de l\'équipe perdante', PLAYERS, max_selections=2)

if st.button('Ajouter Partie'):
    if len(winning_team) == 2 and len(losing_team) == 2:
        update_scores(winning_team, losing_team)
        st.success('Partie ajoutée avec succès!')
    else:
        st.error('Chaque équipe doit avoir exactement 2 joueurs.')

# Calculer et afficher les scores actuels
df = calculate_score(df)
st.header('Scores actuels')
st.table(df[['Player', 'Games_Won', 'Games_Played', 'Score']])

# Sauvegarder le fichier CSV mis à jour
df.to_csv(FILE_PATH, index=False)
