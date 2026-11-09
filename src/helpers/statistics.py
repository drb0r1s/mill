def count_possible_endings(all_game_stats, name):
    wins = 0
    draws = 0
    losses = 0

    for game_stats in all_game_stats:
        if name not in (game_stats["player_1"], game_stats["player_2"]): continue

        if game_stats["winner"] == 0: draws += 1
        elif game_stats["winner_name"] == name: wins += 1
        else: losses += 1

    return wins, draws, losses

def calculate_score(wins, draws, losses):
    games = wins + draws + losses
    return (wins + 0.5 * draws) / games if games else float("nan")

def mean_thinking_time(all_game_stats, name):
    total = 0.0
    moves = 0

    for game_stats in all_game_stats:
        if game_stats["player_1"] == name:
            total += game_stats["player_1_thinking"]
            moves += game_stats["player_1_moves"]

        if game_stats["player_2"] == name:
            total += game_stats["player_2_thinking"]
            moves += game_stats["player_2_moves"]

    return total / moves if moves else float("nan")

# Mean of depth and best fraction.
def mean_stats(all_game_stats, name, key):
    values = []

    for game_stats in all_game_stats:
        for side in ("player_1", "player_2"):
            if game_stats[side] == name and game_stats[f"{key}_{side}"] != "":
                values.append(game_stats[f"{key}_{side}"])

    return sum(values) / len(values) if values else float('nan')