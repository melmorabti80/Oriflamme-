import streamlit as st
from db import load_data, add_game, archive_and_create_new_season, delete_game, create_connection
from game_logic import calculate_scores

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

    # Initialiser les états si non définis
    if 'winning_team' not in st.session_state:
        st.session_state.winning_team = []
    if 'losing_team' not in st.session_state:
        st.session_state.losing_team = []

    # Sélection des joueurs de l'équipe gagnante
    winning_team = st.multiselect(
        'Sélectionnez les joueurs de l\'équipe gagnante',
        options=[player for player in PLAYERS if player not in st.session_state.losing_team],
        default=st.session_state.winning_team,
        max_selections=2,
        on_change=lambda: st.session_state.update({'winning_team': st.session_state.winning_team})
    )

    # Mise à jour de l'état de l'équipe gagnante
    st.session_state.winning_team = winning_team

    # Filtrer les joueurs restants pour l'équipe perdante
    remaining_players = [player for player in PLAYERS if player not in st.session_state.winning_team]

    # Sélection des joueurs de l'équipe perdante
    losing_team = st.multiselect(
        'Sélectionnez les joueurs de l\'équipe perdante',
        options=remaining_players,
        default=st.session_state.losing_team,
        max_selections=2,
        on_change=lambda: st.session_state.update({'losing_team': st.session_state.losing_team})
    )

    # Mise à jour de l'état de l'équipe perdante
    st.session_state.losing_team = losing_team

    if st.button('Ajouter Partie'):
        if len(winning_team) == 2 and len(losing_team) == 2:
            add_game(winning_team, losing_team)
            st.success('Partie ajoutée avec succès!')
            st.session_state.winning_team = []
            st.session_state.losing_team = []
            df = load_data(current_season_id)  # Recharger les données après l'ajout
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')

    # Archiver la saison courante et en démarrer une nouvelle
    if st.button('Archiver la saison'):
        if st.confirm('Voulez-vous vraiment archiver la saison actuelle ?'):
            archive_and_create_new_season()
            st.success('Saison archivée et nouvelle saison créée avec succès!')
            st.experimental_rerun()

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
            df = load_data(current_season_id)  # Recharger les données après la suppression
    else:
        st.write("Aucune partie disponible pour être supprimée.")

    # Afficher les scores
    st.header('Scores actuels')
    if not df.empty:
        scores_df = calculate_scores(df)

        # Remplacer la colonne ID par un classement
        scores_df = scores_df.sort_values(by='Score', ascending=False)
        scores_df['Classement'] = range(1, len(scores_df) + 1)

        # Réorganiser les colonnes pour afficher le classement en premier
        scores_df = scores_df[['Classement', 'Player', 'Games_Won', 'Games_Played', 'Score']]
        st.table(scores_df)
    else:
        st.write("Aucun score disponible pour la saison actuelle.")

    # Statistiques des équipes
    st.header('Statistiques des équipes')
    if not df.empty:
        teams_wins = {}
        teams_losses = {}

        for _, row in df.iterrows():
            winning_team_key = tuple(sorted(row['Winning_Team'].split(', ')))
            losing_team_key = tuple(sorted(row['Losing_Team'].split(', ')))

            teams_wins[winning_team_key] = teams_wins.get(winning_team_key, 0) + 1
            teams_losses[losing_team_key] = teams_losses.get(losing_team_key, 0) + 1

        # Meilleures équipes
        if teams_wins:
            best_winning_team = max(teams_wins, key=teams_wins.get)
            st.write(f"L'équipe qui gagne le plus souvent : {best_winning_team} ({teams_wins[best_winning_team]} victoires)")
        if teams_losses:
            most_losing_team = max(teams_losses, key=teams_losses.get)
            st.write(f"L'équipe qui perd le plus souvent : {most_losing_team} ({teams_losses[most_losing_team]} défaites)")

    # Statistiques des coéquipiers et des séries
    st.header('Statistiques des coéquipiers et des séries')
    if not df.empty:
        for player in PLAYERS:
            teammates_wins = {}
            teammates_losses = {}
            max_wins = 0
            max_losses = 0

            for _, row in df.iterrows():
                winning_team = row['Winning_Team'].split(', ')
                losing_team = row['Losing_Team'].split(', ')

                if player in winning_team:
                    teammate = [p for p in winning_team if p != player][0]
                    teammates_wins[teammate] = teammates_wins.get(teammate, 0) + 1
                    max_wins = max(max_wins, teammates_wins[teammate])

                if player in losing_team:
                    teammate = [p for p in losing_team if p != player][0]
                    teammates_losses[teammate] = teammates_losses.get(teammate, 0) + 1
                    max_losses = max(max_losses, teammates_losses[teammate])

            st.subheader(f"Statistiques de {player}")
            if teammates_wins:
                best_winning_teammate = max(teammates_wins, key=teammates_wins.get)
                st.write(f"Coéquipier avec lequel {player} gagne le plus souvent : {best_winning_teammate} ({teammates_wins[best_winning_teammate]} victoires)")
            if teammates_losses:
                best_losing_teammate = max(teammates_losses, key=teammates_losses.get)
                st.write(f"Coéquipier avec lequel {player} perd le plus souvent : {best_losing_teammate} ({teammates_losses[best_losing_teammate]} défaites)")
