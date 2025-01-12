import streamlit as st
from db import load_data, add_game, archive_and_create_new_season, delete_game, create_connection
from game_logic import calculate_scores
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

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

    # Sélection interactive des joueurs
    selected_winning_team = st.session_state.get("winning_team", [])
    selected_losing_team = st.session_state.get("losing_team", [])
    
    available_players = [p for p in PLAYERS if p not in selected_winning_team + selected_losing_team]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sélectionnez les joueurs gagnants")
        winner = st.selectbox("Ajouter un joueur à l'équipe gagnante", [""] + available_players, key="add_winner")
        if st.button("Ajouter au gagnant", key="add_winner_btn"):
            if winner and winner not in selected_winning_team:
                selected_winning_team.append(winner)
                st.session_state["winning_team"] = selected_winning_team

    with col2:
        st.subheader("Sélectionnez les joueurs perdants")
        loser = st.selectbox("Ajouter un joueur à l'équipe perdante", [""] + available_players, key="add_loser")
        if st.button("Ajouter au perdant", key="add_loser_btn"):
            if loser and loser not in selected_losing_team:
                selected_losing_team.append(loser)
                st.session_state["losing_team"] = selected_losing_team

    st.write("### Équipe gagnante :", selected_winning_team)
    st.write("### Équipe perdante :", selected_losing_team)

    # Vérifier et ajouter la partie
    if st.button('Ajouter Partie'):
        if len(selected_winning_team) == 2 and len(selected_losing_team) == 2:
            add_game(selected_winning_team, selected_losing_team)
            st.success('Partie ajoutée avec succès!')
            st.session_state["winning_team"] = []
            st.session_state["losing_team"] = []
            df = load_data(current_season_id)
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')

    # Afficher les parties enregistrées
    st.header('Parties enregistrées de la saison actuelle')
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")

    # Section pour supprimer une partie
    st.header('Supprimer une partie')
    if not df.empty:
        game_id_to_delete = st.number_input('Entrez l\'ID de la partie à supprimer', min_value=1, max_value=df['GameID'].max(), step=1)
        if st.button('Supprimer Partie'):
            delete_game(game_id_to_delete)
            st.success(f'Partie ID {game_id_to_delete} supprimée avec succès!')
            df = load_data(current_season_id)
    else:
        st.write("Aucune partie disponible pour être supprimée.")

    # Afficher les scores
    st.header('Scores actuels')
    if not df.empty:
        scores_df = calculate_scores(df)
        scores_df = scores_df.sort_values(by='Score', ascending=False)
        scores_df['Classement'] = range(1, len(scores_df) + 1)
        scores_df = scores_df[['Classement', 'Player', 'Games_Won', 'Games_Played', 'Score']]
        st.table(scores_df)

        # Bouton pour télécharger une image du tableau des scores
        st.header("Télécharger les scores")
        if st.button("Générer une image"):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('tight')
            ax.axis('off')
            table = ax.table(cellText=scores_df.values, colLabels=scores_df.columns, loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.auto_set_column_width(col=list(range(len(scores_df.columns))))

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            st.download_button(
                label="Télécharger l'image",
                data=buf,
                file_name="scores_table.png",
                mime="image/png"
            )
    else:
        st.write("Aucun score disponible pour la saison actuelle.")

    # Archiver la saison courante et en démarrer une nouvelle
    st.header("Actions sur la saison")
    if st.button('Archiver la saison'):
        if st.confirm("Êtes-vous sûr de vouloir archiver la saison en cours et en créer une nouvelle ?"):
            archive_and_create_new_season()
            st.success('Saison archivée et nouvelle saison créée avec succès!')
