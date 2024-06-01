import streamlit as st
import pandas as pd
import os

# Chemin du fichier CSV
FILE_PATH = "oriflamme_scores.csv"

# Vérifier si le fichier existe, sinon le créer
if not os.path.exists(FILE_PATH):
    df = pd.DataFrame(columns=['Player', 'Score'])
    df.to_csv(FILE_PATH, index=False)
else:
    df = pd.read_csv(FILE_PATH)

# Fonction pour mettre à jour les scores
def update_scores(winning_team, losing_team):
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
scores = pd.read_csv(FILE_PATH)
st.table(scores)

# Sauvegarder le fichier CSV mis à jour
scores.to_csv(FILE_PATH, index=False)
