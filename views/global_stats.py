import streamlit as st
import pandas as pd
from db import create_connection, load_data, load_archived_data
from game_logic import calculate_scores

def global_stats_view():
    st.title("Statistiques Globales")

    # Charger les données actuelles et archivées
    current_data = load_data()
    archived_data = load_archived_data()

    # Combiner les données pour les statistiques globales
    combined_data = pd.concat([current_data, archived_data], ignore_index=True)

    if combined_data.empty:
        st.write("Aucune donnée disponible pour afficher des statistiques globales.")
        return

    # 1. Total des parties jouées
    total_games = len(combined_data)
    st.subheader(f"Total des parties jouées : {total_games}")

    # 2. Nombre total de saisons archivées
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM seasons WHERE SeasonID IN (SELECT DISTINCT SeasonID FROM archived_games)")
        total_archived_seasons = cursor.fetchone()[0]
        cursor.close()
        connection.close()

    st.subheader(f"Nombre total de saisons archivées : {total_archived_seasons}")

    # Calcul des scores pour toutes les données
    scores = calculate_scores(combined_data)

    # Section 1 : Classement par taux de réussite
    st.header("Classement par taux de réussite")
    scores_sorted_by_win_rate = scores.sort_values(by="Score", ascending=False)
    st.table(scores_sorted_by_win_rate[['Player', 'Games_Played', 'Games_Won', 'Score']])

    # Section 2 : Classement des équipes par victoires et défaites
    st.header("Classement des équipes par victoires et défaites")
    teams_wins = {}
    teams_losses = {}

    for idx, row in combined_data.iterrows():
        winning_team = tuple(sorted(row['Winning_Team'].split(', ')))
        losing_team = tuple(sorted(row['Losing_Team'].split(', ')))

        # Comptabiliser les victoires
        teams_wins[winning_team] = teams_wins.get(winning_team, 0) + 1

        # Comptabiliser les défaites
        teams_losses[losing_team] = teams_losses.get(losing_team, 0) + 1

    # Combiner les statistiques des équipes
    teams_stats = []
    all_teams = set(teams_wins.keys()).union(set(teams_losses.keys()))
    for team in all_teams:
        wins = teams_wins.get(team, 0)
        losses = teams_losses.get(team, 0)
        teams_stats.append({'Team': ', '.join(team), 'Wins': wins, 'Losses': losses})

    teams_df = pd.DataFrame(teams_stats).sort_values(by='Wins', ascending=False)
    st.table(teams_df)

    # Séries de victoires et de défaites par joueur
    series_stats = {
        player: {'max_wins': 0, 'max_losses': 0} for player in scores['Player']
    }

    for player in scores['Player']:
        consecutive_wins = 0
        consecutive_losses = 0

        for idx, row in combined_data.iterrows():
            winning_team = row['Winning_Team'].split(', ')
            losing_team = row['Losing_Team'].split(', ')

            # Gérer les victoires
            if player in winning_team:
                consecutive_wins += 1
                series_stats[player]['max_wins'] = max(series_stats[player]['max_wins'], consecutive_wins)
                consecutive_losses = 0
            # Gérer les défaites
            elif player in losing_team:
                consecutive_losses += 1
                series_stats[player]['max_losses'] = max(series_stats[player]['max_losses'], consecutive_losses)
                consecutive_wins = 0
            else:
                # Réinitialiser si le joueur n'a pas joué
                consecutive_wins = 0
                consecutive_losses = 0

    # 4. Série de victoires la plus longue
    longest_win_streak_player = max(series_stats, key=lambda x: series_stats[x]['max_wins'])
    longest_win_streak = series_stats[longest_win_streak_player]['max_wins']
    st.subheader(f"Série de victoires la plus longue : {longest_win_streak} ({longest_win_streak_player})")

    # 5. Série de défaites la plus longue
    longest_loss_streak_player = max(series_stats, key=lambda x: series_stats[x]['max_losses'])
    longest_loss_streak = series_stats[longest_loss_streak_player]['max_losses']
    st.subheader(f"Série de défaites la plus longue : {longest_loss_streak} ({longest_loss_streak_player})")
