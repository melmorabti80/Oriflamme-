import streamlit as st
import pandas as pd
import os

# Chemin du fichier CSV
FILE_PATH = "oriflamme_scores.csv"

# Fonction pour charger le fichier CSV
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['Player', 'Score'])
    else:
        return pd.DataFrame(columns=['Player', 'Score'])

# Charger les données
df = load_data(FILE_PATH)

# Fonction pour mettre à jour les scores
def update_scores(winning_team, losing_team):
    global df
    for player in winning_team:
        if player in df['Player'].values:
            df.loc[df['Player'] == player, 'Score'] += 1
        else:
            new_row = {'Player': player, 'Score': 1}
            df = df.append(new_row, ignore_index=True)

    for player in losing_team:
        if player not in df['Player'].values:
            new_row = {'Player': player, 'Score': 0}
            df = df.append(new_row, ignore_index=True)

    df.to_csv(FILE_PATH, index=False)

# Interface utilisateur
st.title('Oriflamme Score Tracker')

st.header('Ajouter une nouvelle partie')
winning_team = st.text_input('Équipe gagnante (séparée par des virgules)').split(',')
losing_team = st.text_input('Équipe perdante (séparée par des virgules)').split(',')

if st.button('Ajouter Partie'):
    if len(winning_team) == 2 and len(losing_team) == 2:
        update_scores(winning_team, losing_team)
        st.success('Partie ajoutée avec succès!')
    else:
        st.error('Chaque équipe doit avoir exactement 2 joueurs.')

st.header('Scores actuels')
st.table(df)

# Sauvegarder le fichier CSV mis à jour
df.to_csv(FILE_PATH, index=False)
