import argparse
import math
import itertools

from games.ai_vs_ai import run_tasks, write_csv, count_possible_endings, score, mean_thinking_time, mean_stats

def mcts_props(name, iterations, c):
    return {
        "agent": "mcts",
        "name": name,
        "iterations": iterations,
        "c": c
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
            "player_1": first_player,
            "player_2": second_player
        })

    return tasks

def write_score(all_game_stats, name):
    wins, draws, losses = count_possible_endings(all_game_stats, name)
    return f"{wins:>3} / {draws:>2} / {losses:>3} {score(wins, draws, losses):.3f}"

def main():
    parser = argparse.ArgumentParser(description = "UCT values influence over the game")

    parser.add_argument("--iterations", type = int, default = 200)
    parser.add_argument("--games", type = int, default = 20)
    parser.add_argument("--c", type = float, nargs="+", default=[0.0, 0.25, 0.5, 1.0, math.sqrt(2), 2.0, 4.0])
    parser.add_argument("--c-reference", type = float, default = math.sqrt(2))
    parser.add_argument("--round-robin", action = "store_true")
    parser.add_argument("--workers", type = int, default = None)
    parser.add_argument("--seed", type = int, default = 1)
    parser.add_argument("--out", default = "results/uct_influence")

    args = parser.parse_args()

    names = {}
    for c in args.c: names[c] = f"c = {c:g}"

    random = { "agent": "random", "name": "random" }

    reference = mcts_props(args.reference_c, args.iterations, args.reference_c)

    # Random and reference c

    all_game_stats_random = [] # Random c.
    all_game_stats_reference = [] # Reference c.

    for c in args.c:
        candidate = mcts_props(c, args.iterations, names[c])

        all_game_stats_random += run_tasks(make_tasks("random_c", candidate, random, args.games, args.seed), args.workers, f"{names[c]} vs random")
        all_game_stats_reference += run_tasks(make_tasks("reference_c", candidate, reference, args.games, args.seed), args.workers, f"{names[c]} vs reference")

    write_csv(args.out + "_random_c.csv", all_game_stats_random)
    write_csv(args.out + "_reference_c.cvs", all_game_stats_reference)

    print(f"UCT influence, {args.iterations} iterations / move, {args.games} games per pair. (win = 1, draw = 0.5, loss = 0)\n")

    header = f"{'c':>7} | {'random':^17} | {'reference c = ' + format(args.reference_c, 'g') + ')':^17} | {'tree depth':>10} | {'best-move visit share':>20} | {'s / move':>7}"
    
    print(header)
    print("-" * len(header))

    for c in args.c:
        name = names[c]
        print(f"{c:>7g} | {write_score(all_game_stats_random, name)} | {write_score(all_game_stats_reference, name)} | {mean_stats(all_game_stats_random + all_game_stats_reference, name, "depth"):>10.2f} | {mean_stats(all_game_stats_random + all_game_stats_reference, name, "best_move_fraction"):>21.3f} | {mean_thinking_time(all_game_stats_random + all_game_stats_reference, name):>7.3f}")

    # Optional and round-robin AI

    if args.round_robin:
        all_game_stats_rr = []

        for first_c, second_c in itertools.combinations(args.c, 2):
            first_candidate = mcts_props(first_c, args.iterations, names[first_c])
            second_candidate = mcts_props(second_c, args.iterations, names[second_c])

            all_game_stats_rr += run_tasks(make_tasks("round_robin", first_candidate, second_candidate, args.games, args.seed), args.workers, f"{names[first_c]} vs {names[second_c]}")

        write_csv(args.out + "_round_robin.csv", all_game_stats_rr)

        print("\nRound robin between c values:")
        print(f"{'':>7}" + " ".join(f"{names[c]:>8}" for c in args.c) + "total")

        for first_c in args.c:
            cells = []
            total = 0.0

            for second_c in args.c:
                if first_c == second_c:
                    cells.append(f"{'-':>8}")
                    continue

                pair = []
                        
                for game_stats in all_game_stats_rr:
                    if {game_stats["player_1"], game_stats["player_2"]} == {names[first_c], names[second_c]}:
                        pair.append(game_stats)

                current_score = score(*count_possible_endings(pair, names[first_c]))
                total += current_score

                cells.append(f"{current_score:>8.2f}")

            print(f"{names[first_c]:>7}" + " ".join(cells) + f"{total:.2f}")

if __name__ == "__main__": main()