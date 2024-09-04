import pandas as pd

PLAYERS = ['Meimine', 'Hila', 'Hassan', 'Wahed', 'Morabti', 'Khalil']

def calculate_scores(df):
    players_stats = {player: {'Games_Won': 0, 'Games_Played': 0} for player in PLAYERS}
    teammates_wins = {player: {} for player in PLAYERS}
    teammates_losses = {player: {} for player in PLAYERS}

    for _, row in df.iterrows():
        winning_team = row['Winning_Team'].split(', ')
        losing_team = row['Losing_Team'].split(', ')

        for player in winning_team:
            players_stats[player]['Games_Won'] += 1
            players_stats[player]['Games_Played'] += 1
            teammate = winning_team[1] if winning_team[0] == player else winning_team[0]
            if teammate not in teammates_wins[player]:
                teammates_wins[player][teammate] = 0
            teammates_wins[player][teammate] += 1

        for player in losing_team:
            players_stats[player]['Games_Played'] += 1
            teammate = losing_team[1] if losing_team[0] == player else losing_team[0]
            if teammate not in teammates_losses[player]:
                teammates_losses[player][teammate] = 0
            teammates_losses[player][teammate] += 1

    # Ajouter les meilleurs coéquipiers
    for player in PLAYERS:
        players_stats[player]['Best_Teammate_Wins'] = max(teammates_wins[player], key=teammates_wins[player].get, default='N/A')
        players_stats[player]['Best_Teammate_Losses'] = max(teammates_losses[player], key=teammates_losses[player].get, default='N/A')

    scores = pd.DataFrame([{
        'Player': player, 
        'Games_Won': stats['Games_Won'], 
        'Games_Played': stats['Games_Played'], 
        'Score': round((stats['Games_Won'] / stats['Games_Played']) * 100, 2) if stats['Games_Played'] > 0 else 0,
        'Best_Teammate_Wins': stats['Best_Teammate_Wins'],
        'Best_Teammate_Losses': stats['Best_Teammate_Losses']
    } for player, stats in players_stats.items()])
    
    return scores

