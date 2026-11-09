import argparse
import itertools

from data.difficulties import DIFFICULTIES
from games.ai_vs_ai import run_tasks, write_csv, count_possible_endings, score, mean_thinking_time

def main():
    parser = argparse.ArgumentParser(description = "AI difficulties competition")
    
    parser.add_argument("--difficulties", nargs="+", default=list(DIFFICULTIES))
    parser.add_argument("--games", type = int, default = 20) # Games per pair of levels
    parser.add_argument("--workers", type = int, default = None)
    parser.add_argument("--seed", type = int, default = 1)
    parser.add_argument("--out", default = "results/difficulty_competition.cvs")

    args = parser.parse_args()

    props = {}
    for difficulty in args.difficulties: props[difficulty] = dict(DIFFICULTIES[difficulty], difficulty = difficulty)

    all_game_stats = []

    for first_difficulty, second_difficulty in itertools.combinations(args.difficulties, 2):
        play_tasks = []

        for game in range(args.games):
            if game % 2 == 0:
                player1 = first_difficulty
                player2 = second_difficulty

            else:
                player1 = second_difficulty
                player2 = first_difficulty

            play_tasks.append({
                "id": "difficulty_competition",
                "game": game,
                "seed": f"{args.seed} difficulty_competition {player1} {player2} {game}",
                "props_1": props[player1],
                "props_2": props[player2]
            })

        all_game_stats += run_tasks(play_tasks, args.workers)

    write_csv(args.out, all_game_stats)

    print(f"Difficulty competition, {args.games} games per pair. (win = 1, draw = 0.5, loss = 0)\n")
    print(f"{'':>8}" + " ".join(f"{difficulty}" for difficulty in args.difficulties) + f"{'points':>8}")

    for first_difficulty in args.difficulties:
        cells = []
        points = 0.0

        for second_difficulty in args.difficulties:
            if first_difficulty == second_difficulty:
                cells.append(f"{'-':>8}")
                continue

            pair = []

            for game_stats in all_game_stats:
                if {game_stats["player_1"], game_stats["player_2"]} == {first_difficulty, second_difficulty}:
                    pair.append(game_stats)

            wins, draws, losses = count_possible_endings(pair, first_difficulty)
            points += wins + 0.5 * draws

            cells.append(f"{score(wins, draws, losses):>8.2f}")

        print(f"{first_difficulty:>8}" + " ".join(cells) + f"{points:>8.1f}")

    print("Wins/Draws/Losses Pairs:")

    for first_difficulty, second_difficulty in itertools.combinations(args.difficulties, 2):
        pair = []
        
        for game_stats in all_game_stats:
            if {game_stats["player_1"], game_stats["player_2"]} == {first_difficulty, second_difficulty}:
                pair.append(game_stats)

        wins, draws, losses = count_possible_endings(pair, first_difficulty)
        print(f"{first_difficulty:>7} vs {second_difficulty:<7} {wins:>3} / {draws:>2} / {losses:>3}")

    print("\nMean thinking time per move:")

    for difficulty in args.difficulties:
        print(f"{difficulty:>8}: {mean_thinking_time(all_game_stats, difficulty):7.3f}s")

if __name__ == "__main__": main()