import streamlit as st
from db import load_data, add_game, archive_and_create_new_season, delete_game, create_connection
from game_logic import calculate_scores, calculate_team_statistics

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

    # Ajouter une partie
    add_game_section(df, current_season_id)

    # Archiver la saison
    archive_season_section()

    # Afficher les parties enregistrées
    display_games_section(df)

    # Supprimer une partie
    delete_game_section(df, current_season_id)

    # Afficher les scores
    display_scores_section(df)

    # Statistiques des équipes
    display_team_statistics(df)

    # Statistiques des coéquipiers et séries
    display_player_statistics(df)


def add_game_section(df, current_season_id):
    st.header('Ajouter une nouvelle partie')

    winning_team = st.multiselect('Sélectionnez les joueurs de l\'équipe gagnante', PLAYERS, max_selections=2)
    remaining_players = [player for player in PLAYERS if player not in winning_team]
    losing_team = st.multiselect('Sélectionnez les joueurs de l\'équipe perdante', remaining_players, max_selections=2)

    if st.button('Ajouter Partie'):
        if len(winning_team) == 2 and len(losing_team) == 2:
            add_game(winning_team, losing_team)
            st.success('Partie ajoutée avec succès!')
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')


def archive_season_section():
    st.header('Archiver la saison')
    if st.button('Archiver la saison et démarrer une nouvelle saison'):
        archive_and_create_new_season()
        st.success('Saison archivée et nouvelle saison créée avec succès!')


def display_games_section(df):
    st.header('Parties enregistrées de la saison actuelle')
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")


def delete_game_section(df, current_season_id):
    st.header('Supprimer une partie')
    if not df.empty:
        game_id_to_delete = st.number_input('Entrez l\'ID de la partie à supprimer', min_value=1, max_value=df['GameID'].max(), step=1)

        if st.button('Supprimer Partie'):
            delete_game(game_id_to_delete)
            st.success(f'Partie ID {game_id_to_delete} supprimée avec succès!')
    else:
        st.write("Aucune partie disponible pour être supprimée.")


def display_scores_section(df):
    st.header('Scores actuels')
    if not df.empty:
        scores_df = calculate_scores(df)
        scores_df = scores_df.sort_values(by='Score', ascending=False)
        scores_df['Classement'] = range(1, len(scores_df) + 1)
        scores_df = scores_df[['Classement', 'Player', 'Games_Won', 'Games_Played', 'Score']]
        st.table(scores_df)
    else:
        st.write("Aucun score disponible pour la saison actuelle.")


def display_team_statistics(df):
    st.header('Statistiques des équipes')
    if not df.empty:
        team_stats = calculate_team_statistics(df)
        st.write(f"L'équipe qui gagne le plus souvent : {team_stats['best_winning_team']} ({team_stats['best_winning_team_count']} victoires)")
        st.write(f"L'équipe qui perd le plus souvent : {team_stats['best_losing_team']} ({team_stats['best_losing_team_count']} défaites)")
    else:
        st.write("Aucune donnée disponible pour les statistiques des équipes.")


def display_player_statistics(df):
    st.header('Statistiques des coéquipiers et des séries')
    if not df.empty:
        for player in PLAYERS:
            player_stats = calculate_player_statistics(player, df)
            st.subheader(f"Statistiques de {player}")
            st.write(f"Coéquipier avec lequel {player} gagne le plus souvent : {player_stats['best_winning_teammate']}")
            st.write(f"Coéquipier avec lequel {player} perd le plus souvent : {player_stats['best_losing_teammate']}")
            st.write(f"Série de victoires la plus longue : {player_stats['max_consecutive_wins']}")
            st.write(f"Série de défaites la plus longue : {player_stats['max_consecutive_losses']}")
    else:
        st.write("Pas assez de données pour afficher des statistiques.")


# Vous devrez définir `calculate_team_statistics` et `calculate_player_statistics` dans `game_logic.py`.
