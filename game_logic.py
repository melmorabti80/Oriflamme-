import pandas as pd

PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

def calculate_scores(df):
    # Initialisation des statistiques
    players_stats = {player: {'Games_Won': 0, 'Games_Played': 0} for player in PLAYERS}
    teammates_wins = {player: {} for player in PLAYERS}
    teammates_losses = {player: {} for player in PLAYERS}
    teams_wins = {}
    teams_losses = {}

    # Parcourir les données des parties
    for _, row in df.iterrows():
        winning_team = tuple(sorted(row['Winning_Team'].split(', ')))  # Trier pour éviter les doublons
        losing_team = tuple(sorted(row['Losing_Team'].split(', ')))

        # Comptabiliser les victoires et défaites d'équipe
        teams_wins[winning_team] = teams_wins.get(winning_team, 0) + 1
        teams_losses[losing_team] = teams_losses.get(losing_team, 0) + 1

        # Mises à jour des stats individuelles
        for player in winning_team:
            players_stats[player]['Games_Won'] += 1
            players_stats[player]['Games_Played'] += 1
            teammate = [p for p in winning_team if p != player][0]
            teammates_wins[player][teammate] = teammates_wins[player].get(teammate, 0) + 1

        for player in losing_team:
            players_stats[player]['Games_Played'] += 1
            teammate = [p for p in losing_team if p != player][0]
            teammates_losses[player][teammate] = teammates_losses[player].get(teammate, 0) + 1

    # Calculer les meilleurs coéquipiers
    for player in PLAYERS:
        players_stats[player]['Best_Teammate_Wins'] = max(teammates_wins[player], key=teammates_wins[player].get, default='N/A')
        players_stats[player]['Best_Teammate_Losses'] = max(teammates_losses[player], key=teammates_losses[player].get, default='N/A')

    # Trouver les équipes avec le plus de victoires et de défaites
    best_winning_team = max(teams_wins, key=teams_wins.get, default=None)
    best_losing_team = max(teams_losses, key=teams_losses.get, default=None)

    # Créer un DataFrame des scores
    scores = pd.DataFrame([{
        'Player': player,
        'Games_Won': stats['Games_Won'],
        'Games_Played': stats['Games_Played'],
        'Score (%)': round((stats['Games_Won'] / stats['Games_Played']) * 100, 2) if stats['Games_Played'] > 0 else 0,
        'Best_Teammate_Wins': stats['Best_Teammate_Wins'],
        'Best_Teammate_Losses': stats['Best_Teammate_Losses']
    } for player, stats in players_stats.items()])

    # Ajouter les statistiques des équipes au DataFrame des résultats globaux
    if best_winning_team:
        scores.loc[len(scores)] = {
            'Player': f"Equipe gagnante : {', '.join(best_winning_team)}",
            'Games_Won': teams_wins[best_winning_team],
            'Games_Played': "N/A",
            'Score (%)': "N/A",
            'Best_Teammate_Wins': "N/A",
            'Best_Teammate_Losses': "N/A"
        }
    if best_losing_team:
        scores.loc[len(scores)] = {
            'Player': f"Equipe perdante : {', '.join(best_losing_team)}",
            'Games_Won': "N/A",
            'Games_Played': teams_losses[best_losing_team],
            'Score (%)': "N/A",
            'Best_Teammate_Wins': "N/A",
            'Best_Teammate_Losses': "N/A"
        }

    return scores
