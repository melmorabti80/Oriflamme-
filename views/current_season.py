import streamlit as st
from db import load_data, add_game, archive_and_create_new_season
from game_logic import calculate_scores
import pandas as pd

PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

def current_season_view():
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
            df = load_data(current_season_id)
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')

    # Afficher les parties enregistrées
    st.header('Parties enregistrées de la saison actuelle')
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")

    # Afficher les scores
    st.header('Scores actuels')
    if not df.empty:
        scores_df = calculate_scores(df)
        st.table(scores_df)
    else:
        st.write("Aucun score disponible pour la saison actuelle.")

    # Archiver la saison
    if st.button('Archiver la saison et démarrer une nouvelle saison'):
        archive_and_create_new_season()
        st.success('Saison archivée et nouvelle saison créée avec succès!')

