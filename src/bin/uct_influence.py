# Exploring how different values of the UCT function affect the gameplay.

import argparse
import math

from src.helpers.task import run_tasks
from src.helpers.csv import write_csv
from src.helpers.statistics import count_possible_endings, calculate_score, mean_thinking_time, mean_stats

def mcts_props(c, iterations, name):
    return {
        "agent": "mcts",
        "c": c,
        "iterations": iterations,
        "name": name
    }

def make_tasks(id, player1, player2, games, seed):
    tasks = []

    for game in range(games):
        if game % 2 == 0:
            first_player = player1
            second_player = player2
        
        else:
            first_player = player2
            second_player = player1

        tasks.append({
            "id": id,
            "game": game,
            "seed": f"{seed} {id} {player1["name"]} {player2["name"]} {game}",
            "player_1_props": first_player,
            "player_2_props": second_player
        })

    return tasks

def write_score(all_game_stats, name):
    wins, draws, losses = count_possible_endings(all_game_stats, name)
    return f"{wins:>3} / {draws:>2} / {losses:>3} {calculate_score(wins, draws, losses):.3f}"

def main():
    parser = argparse.ArgumentParser(description = "UCT values influence over the game")

    parser.add_argument("--iterations", type = int, default = 200)
    parser.add_argument("--games", type = int, default = 20)
    parser.add_argument("--c", type = float, nargs="+", default=[0.0, 0.25, 0.5, 1.0, math.sqrt(2), 2.0, 4.0])
    parser.add_argument("--reference-c", type = float, default = math.sqrt(2))
    parser.add_argument("--round-robin", action = "store_true")
    parser.add_argument("--workers", type = int, default = None)
    parser.add_argument("--seed", type = int, default = 1)
    parser.add_argument("--out", default = "results/uct_influence")

    args = parser.parse_args()

    names = {}
    for c in args.c: names[c] = f"c = {c:g}"

    random = { "agent": "random", "name": "random" }

    reference = mcts_props(args.reference_c, args.iterations, f"reference c = {args.reference_c:g}")

    # Random and reference c

    all_game_stats_random = [] # Random c.
    all_game_stats_reference = [] # Reference c.

    for c in args.c:
        candidate = mcts_props(c, args.iterations, names[c])

        all_game_stats_random += run_tasks(make_tasks("random_c", candidate, random, args.games, args.seed), args.workers, f"{names[c]} vs random")
        all_game_stats_reference += run_tasks(make_tasks("reference_c", candidate, reference, args.games, args.seed), args.workers, f"{names[c]} vs reference")

    write_csv(args.out + "_random_c.csv", all_game_stats_random)
    write_csv(args.out + "_reference_c.csv", all_game_stats_reference)

    print(f"UCT influence, {args.iterations} iterations / move, {args.games} games per pair. (win = 1, draw = 0.5, loss = 0)\n")

    header = f"{'c':>7} | {'random':^20} | {'reference (c = ' + format(args.reference_c, 'g') + ')':^20} | {'tree depth':>10} | {'best-move visit share':>21} | {'s / move':>7}"
    
    print(header)
    print("-" * len(header))

    for c in args.c:
        name = names[c]
        print(f"{c:>7g} | {write_score(all_game_stats_random, name)} | {write_score(all_game_stats_reference, name)} | {mean_stats(all_game_stats_random + all_game_stats_reference, name, "mean_tree_depth"):>10.2f} | {mean_stats(all_game_stats_random + all_game_stats_reference, name, "mean_best_visit_fraction"):>21.3f} | {mean_thinking_time(all_game_stats_random + all_game_stats_reference, name):>7.3f}")

if __name__ == "__main__": main()