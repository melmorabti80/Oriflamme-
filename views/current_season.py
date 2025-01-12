import streamlit as st
from streamlit_drag_and_drop import drag_and_drop
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

    # Gestion des équipes avec drag-and-drop
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Joueurs disponibles")
        players_pool = drag_and_drop(
            items=PLAYERS,
            key="players_pool",
        )

    with col2:
        st.subheader("Équipe gagnante")
        winning_team = drag_and_drop(
            items=[],
            allow_duplicates=False,
            max_items=2,
            source_key="players_pool",
            key="winning_team"
        )

    with col3:
        st.subheader("Équipe perdante")
        losing_team = drag_and_drop(
            items=[],
            allow_duplicates=False,
            max_items=2,
            source_key="players_pool",
            key="losing_team"
        )

    # Ajouter une partie
    if st.button("Ajouter Partie"):
        if len(winning_team) == 2 and len(losing_team) == 2:
            add_game(winning_team, losing_team)
            st.success("Partie ajoutée avec succès!")
            df = load_data(current_season_id)  # Recharger les données après l'ajout
        else:
            st.error("Chaque équipe doit avoir exactement 2 joueurs.")

    # Afficher les parties enregistrées
    st.header("Parties enregistrées de la saison actuelle")
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")

    # Section pour supprimer une partie
    st.header("Supprimer une partie")
    if not df.empty:
        game_id_to_delete = st.number_input(
            "Entrez l'ID de la partie à supprimer",
            min_value=1,
            max_value=df['GameID'].max(),
            step=1
        )

        if st.button("Supprimer Partie"):
            delete_game(game_id_to_delete)
            st.success(f"Partie ID {game_id_to_delete} supprimée avec succès!")
            df = load_data(current_season_id)  # Recharger les données après la suppression
    else:
        st.write("Aucune partie disponible pour être supprimée.")

    # Afficher les scores
    st.header("Scores actuels")
    if not df.empty:
        scores_df = calculate_scores(df)

        # Remplacer la colonne ID par un classement
        scores_df = scores_df.sort_values(by="Score", ascending=False)
        scores_df["Classement"] = range(1, len(scores_df) + 1)

        # Réorganiser les colonnes pour afficher le classement en premier
        scores_df = scores_df[["Classement", "Player", "Games_Won", "Games_Played", "Score"]]
        st.table(scores_df)

        # Ajout d'un bouton pour télécharger une image du tableau des scores
        st.header("Télécharger les scores")
        if st.button("Générer une image"):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('tight')
            ax.axis('off')
            table = ax.table(
                cellText=scores_df.values,
                colLabels=scores_df.columns,
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.auto_set_column_width(col=list(range(len(scores_df.columns))))

            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            st.download_button(
                label="Télécharger l'image",
                data=buf,
                file_name="scores_table.png",
                mime="image/png"
            )
    else:
        st.write("Aucun score disponible pour la saison actuelle.")

    # Archiver la saison courante et démarrer une nouvelle saison
    st.header("Actions sur la saison")
    if st.button("Archiver la saison"):
        if st.confirm("Êtes-vous sûr de vouloir archiver la saison en cours et en créer une nouvelle ?"):
            archive_and_create_new_season()
            st.success("Saison archivée et nouvelle saison créée avec succès!")
