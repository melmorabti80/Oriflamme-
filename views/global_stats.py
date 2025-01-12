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

    # 3. Joueur avec le plus de victoires
    top_winner = scores.loc[scores['Games_Won'].idxmax()]
    st.subheader(f"Joueur avec le plus de victoires : {top_winner['Player']} ({top_winner['Games_Won']} victoires)")

    # 4. Joueur avec le plus de défaites
    scores['Losses'] = scores['Games_Played'] - scores['Games_Won']
    top_loser = scores.loc[scores['Losses'].idxmax()]
    st.subheader(f"Joueur avec le plus de défaites : {top_loser['Player']} ({top_loser['Losses']} défaites)")

    # 5. Joueur avec le plus grand rapport matchs gagnés/nombre de parties totales jouées
    scores['Win_Rate'] = (scores['Games_Won'] / scores['Games_Played']).fillna(0)
    top_win_rate_player = scores.loc[scores['Win_Rate'].idxmax()]
    st.subheader(f"Joueur avec le plus grand taux de victoires : {top_win_rate_player['Player']} ({top_win_rate_player['Win_Rate']:.2%})")

    # 6. Joueur avec le plus grand rapport matchs perdus/nombre de parties totales jouées
    scores['Loss_Rate'] = (scores['Losses'] / scores['Games_Played']).fillna(0)
    top_loss_rate_player = scores.loc[scores['Loss_Rate'].idxmax()]
    st.subheader(f"Joueur avec le plus grand taux de défaites : {top_loss_rate_player['Player']} ({top_loss_rate_player['Loss_Rate']:.2%})")

    # Statistiques des équipes
    teams_wins = {}
    teams_losses = {}

    for idx, row in combined_data.iterrows():
        winning_team = tuple(sorted(row['Winning_Team'].split(', ')))
        losing_team = tuple(sorted(row['Losing_Team'].split(', ')))

        # Comptabiliser les victoires
        teams_wins[winning_team] = teams_wins.get(winning_team, 0) + 1

        # Comptabiliser les défaites
        teams_losses[losing_team] = teams_losses.get(losing_team, 0) + 1

    # 7. Meilleure équipe gagnante
    if teams_wins:
        best_winning_team = max(teams_wins, key=teams_wins.get)
        st.subheader(f"L'équipe qui gagne le plus souvent : {best_winning_team} ({teams_wins[best_winning_team]} victoires)")

    # 8. Équipe la plus perdante
    if teams_losses:
        most_losing_team = max(teams_losses, key=teams_losses.get)
        st.subheader(f"L'équipe qui perd le plus souvent : {most_losing_team} ({teams_losses[most_losing_team]} défaites)")

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

    # 9. Joueur avec la série de victoires la plus longue
    longest_win_streak_player = max(series_stats, key=lambda x: series_stats[x]['max_wins'])
    longest_win_streak = series_stats[longest_win_streak_player]['max_wins']
    st.subheader(f"Série de victoires la plus longue : {longest_win_streak} ({longest_win_streak_player})")

    # 10. Joueur avec la série de défaites la plus longue
    longest_loss_streak_player = max(series_stats, key=lambda x: series_stats[x]['max_losses'])
    longest_loss_streak = series_stats[longest_loss_streak_player]['max_losses']
    st.subheader(f"Série de défaites la plus longue : {longest_loss_streak} ({longest_loss_streak_player})")
