import argparse
import random as r
import time
import statistics

from famnit_gym.envs import mill

from mcts import MCTS
from games.ai_vs_ai import write_csv

INTERVALS = [
    ("[EARLY] placing [0, 9]", 0, 9),
    ("[EARLY] late placing [10, 17]", 10, 17),
    ("[MIDDLE] moving [20, 39]", 20, 39),
    ("[LATE] moving or flying [40, 79]", 40, 79)
]

def random_positions(count, bottom, top, random):
    env = mill.env()
    env.reset()

    positions = []

    while len(positions) < count:
        model = mill.transition_model(env)
        target = random.randint(bottom, top)

        player = 1
        turns = 0

        while turns < target and not model.game_over():
            moves = model.legal_moves(player)
            model.make_move(player, moves[random.randrange(len(moves))])

            player = 3 - player
            turns += 1

        if not model.game_over(): positions.append((model, player, turns))

    env.close()

    return positions

def main():
    parser = argparse.ArgumentParser(description = "Mill: Computation time / AI difficulty")

    parser.add_argument("--iterations", type = int, nargs = "+", default = [10, 25, 50, 100, 200, 500, 1000])
    parser.add_argument("--positions", type = int, default = 10) # Positions per interval
    parser.add_argument("--seed", type = int, default = 1)
    parser.add_argument("--out", default = "results/difficulty_computation.csv")

    args = parser.parse_args()

    random = r.Random(args.seed)

    intervals = {}
    for name, bottom, top in INTERVALS: intervals[name] = random_positions(args.positions, bottom, top, random)

    all_game_stats = []

    for name, positions in intervals.items():
        for iterations in args.iterations:
            times = []

            for index, (model, player, turns) in enumerate(positions):
                mcts = MCTS(iterations = iterations, random = r.Random(f"{args.seed} {name} {iterations} {index}"))

                start = time.perf_counter()
                mcts.search(model, player, turns)
                times.append(time.perf_counter() - start)

            mean_time = statistics.mean(times)
            ms_per_iteration = 1000 * mean_time / iterations

            all_game_stats.append({
                "positions": name,
                "iterations": iterations,
                "mean_time": mean_time,
                "standard_deviation_time": statistics.stdev(times) if len(times) > 1 else 0.0,
                "ms_per_iteration": ms_per_iteration
            })

            print(f"{name:<26} {iterations:>5} iterations: {mean_time:8.3f} s / move, {1000 * mean_time / iterations:.2f} ms / iteration", flush = True)

    write_csv(args.out, all_game_stats)

    print("\nMean seconds per move")
    print(f"{"iterations":>10} " + " ".join(f"{name[:24]:>25.3f}" for name, _, _ in INTERVALS))

    for iterations in args.iterations:
        cells = []

        for name, _, _ in INTERVALS:
            for game_stats in all_game_stats:
                if game_stats["positions"] == name and game_stats["iterations"] == iterations: cells.append(game_stats["mean_time"])

        print(f"{iterations:>10}" + " ".join(f"{cell:>25}" for cell in cells))

if __name__ == "__main__": main()