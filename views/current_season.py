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

    # Sélection des joueurs de l'équipe gagnante
    winning_team = st.multiselect('Sélectionnez les joueurs de l\'équipe gagnante', PLAYERS, max_selections=2)

    # Filtrer la liste des joueurs perdants en excluant les joueurs de l'équipe gagnante
    remaining_players = [player for player in PLAYERS if player not in winning_team]
    losing_team = st.multiselect('Sélectionnez les joueurs de l\'équipe perdante', remaining_players, max_selections=2)

    if st.button('Ajouter Partie'):
        if len(winning_team) == 2 and len(losing_team) == 2:
            add_game(winning_team, losing_team)
            st.success('Partie ajoutée avec succès!')
            df = load_data(current_season_id)  # Recharger les données après l'ajout
        else:
            st.error('Chaque équipe doit avoir exactement 2 joueurs.')

    # Afficher les parties enregistrées
    st.header('Parties enregistrées de la saison actuelle')
    if not df.empty:
        st.table(df)
    else:
        st.write("Aucune partie enregistrée pour la saison actuelle.")

    # Section pour supprimer une partie à l'aide d'un formulaire
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

    # Archiver la saison
    if st.button('Archiver la saison et démarrer une nouvelle saison'):
        archive_and_create_new_season()
        st.success('Saison archivée et nouvelle saison créée avec succès!')

    # Statistiques des coéquipiers et adversaires
    st.header('Statistiques des coéquipiers et adversaires')
    if not df.empty:
        for player in PLAYERS:
            teammates_wins = {}
            teammates_losses = {}
            opponents_wins = {}
            opponents_losses = {}
            consecutive_wins = 0
            consecutive_losses = 0
            max_consecutive_wins = 0
            max_consecutive_losses = 0
            last_game_result = None

            for idx, row in df.iterrows():
                winning_team = row['Winning_Team'].split(', ')
                losing_team = row['Losing_Team'].split(', ')

                # Gagner avec un coéquipier
                if player in winning_team:
                    teammate = [p for p in winning_team if p != player][0]
                    teammates_wins[teammate] = teammates_wins.get(teammate, 0) + 1

                    # Gagner contre un adversaire
                    for opponent in losing_team:
                        opponents_wins[opponent] = opponents_wins.get(opponent, 0) + 1

                    # Gestion des séries de victoires et défaites
                    if last_game_result == 'win':
                        consecutive_wins += 1
                    else:
                        consecutive_wins = 1
                    last_game_result = 'win'
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                    consecutive_losses = 0

                # Perdre avec un coéquipier
                if player in losing_team:
                    teammate = [p for p in losing_team if p != player][0]
                    teammates_losses[teammate] = teammates_losses.get(teammate, 0) + 1

                    # Perdre contre un adversaire
                    for opponent in winning_team:
                        opponents_losses[opponent] = opponents_losses.get(opponent, 0) + 1

                    # Gestion des séries de défaites
                    if last_game_result == 'loss':
                        consecutive_losses += 1
                    else:
                        consecutive_losses = 1
                    last_game_result = 'loss'
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                    consecutive_wins = 0

            st.subheader(f"Statistiques de {player}")

            # Meilleur coéquipier (gagnant)
            if teammates_wins:
                best_winning_teammate = max(teammates_wins, key=teammates_wins.get)
                st.write(f"Coéquipier avec lequel {player} gagne le plus souvent : {best_winning_teammate} ({teammates_wins[best_winning_teammate]} victoires)")
            else:
                st.write(f"{player} n'a pas encore gagné avec un coéquipier spécifique.")

            # Meilleur coéquipier (perdant)
            if teammates_losses:
                best_losing_teammate = max(teammates_losses, key=teammates_losses.get)
                st.write(f"Coéquipier avec lequel {player} perd le plus souvent : {best_losing_teammate} ({teammates_losses[best_losing_teammate]} défaites)")
            else:
                st.write(f"{player} n'a pas encore perdu avec un coéquipier spécifique.")

            # Adversaire contre lequel on gagne le plus souvent
            if opponents_wins:
                best_winning_opponent = max(opponents_wins, key=opponents_wins.get)
                st.write(f"Adversaire avec lequel {player} gagne le plus souvent : {best_winning_opponent} ({opponents_wins[best_winning_opponent]} victoires)")

            # Adversaire contre lequel on perd le plus souvent
            if opponents_losses:
                best_losing_opponent = max(opponents_losses, key=opponents_losses.get)
                st.write(f"Adversaire avec lequel {player} perd le plus souvent : {best_losing_opponent} ({opponents_losses[best_losing_opponent]} défaites)")

            # Séries de victoires et défaites
            st.write(f"Série de victoires la plus longue : {max_consecutive_wins}")
            st.write(f"Série de défaites la plus longue : {max_consecutive_losses}")
    else:
        st.write("Pas assez de données pour afficher des statistiques.")
