import os
import time
import sys
import multiprocessing
import csv

from famnit_gym.envs import mill

from agents import build_agent

def agent_play(agent1, agent2, render_mode = None):
    agents = { "agent_1": agent1, "agent_2": agent2 }

    env = mill.env(render_mode = render_mode)
    env.reset()

    thinking = { "agent_1": 0.0, "agent_2": 0.0 }
    moves = { "agent_1": 0, "agent_2": 0 }
    captures = { "agent_1": 0, "agent_2": 0 }

    turns = 0

    for name in env.agent_iter():
        _, _, termination, truncation, info = env.last()

        if termination or truncation: break

        player = 1
        if name == "agent_2": player = 2

        # info["move"] - 1 in order to get total number of rounds (round = 2 * turn).
        # We have to subtract 1 from info["move"], because "move" starts from 1.
        # args.side - 1 represents the current round being played (its progress).
        turns = 2 * (info["move"] - 1) + player - 1

        model = mill.transition_model(env.unwrapped)

        start = time.perf_counter()

        move = agents[name].play(model, player, turns)

        thinking[name] += time.perf_counter() - start

        moves[name] += 1
        if move[2] > 0: captures[name] += 1

        env.step(move)

        turns += 1

    final_model = mill.transition_model(env.unwrapped)

    env.close()

    if final_model.get_phase(1) == "lost": winner = 2
    if final_model.get_phase(2) == "lost": winner = 1
    else: winner = 0

    return {
        "winner": "agent_1" if winner == 1 else "agent_2",
        "turns": turns,
        "agent_1_pieces": final_model.count_pieces(1),
        "agent_2_pieces": final_model.count_pieces(2),
        "agent_1_thinking": thinking["agent_1"],
        "agent_2_thinking": thinking["agent_2"],
        "agent_1_moves": moves["agent_1"],
        "agent_2_moves": moves["agent_2"],
        "agent_1_captures": moves["agent_1"],
        "agent_2_captures": moves["agent_2"],
    }

def play_task(task):
    agent1 = build_agent(task["agent_1_props"], f"agent_1_seed:{task["seed"]}")
    agent2 = build_agent(task["agent_2_props"], f"agent_2_seed:{task["seed"]}")

    result = agent_play(agent1, agent2)

    game_stats = {
        "tag": task.get("tag"),
        "game": task["game"],
        "seed": task["seed"],
        "agent_1": agent1.name,
        "agent_2": agent2.name,
        "winner_name": None
    }

    game_stats.update(result)

    if result["winner"] == 1: game_stats["winner_name"] = agent1.name
    if result["winner"] == 2: game_stats["winner_name"] = agent2.name
    else: game_stats["winner_name"] = "neither"

    for id, agent in (("agent_1", agent1), ("agent_2", agent2)):
        report = agent.report()

        game_stats[f"{id}_mistakes"] = report.get("mistakes")
        game_stats[f"{id}_mean_tree_depth"] = report.get("mean_tree_depth")
        game_stats[f"{id}_mean_best_visit_fraction"] = report.get("mean_best_visit_fraction")

    return game_stats

def run_tasks(tasks, workers = None):
    workers = workers or os.cpu_count() or 1

    all_game_stats = []
    total_tasks_amunt = len(tasks)

    start = time.perf_counter()

    def progress(finished_tasks_amount):
        elapsed = time.perf_counter() - start
        print(f"{finished_tasks_amount}/{total_tasks_amunt} games, {elapsed:.0f}s", file = sys.stderr, flush = True)

    if workers <= 1:
        for index, task in enumerate(tasks, 1):
            all_game_stats.append(play_task(task))
            progress(index)

    else:
        with multiprocessing.Pool(workers) as pool:
            for index, game_stats in enumerate(pool.imap(play_task, tasks), 1):
                all_game_stats.append(game_stats)
                progress(index)

    print(file = sys.stderr)

    return all_game_stats

def write_csv(path, all_game_stats):
    if not all_game_stats: return

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok = True)

    with open(path, "w", newline = "") as file:
        writer = csv.DictWriter(file, fieldnames = list(all_game_stats[0].keys()))
        writer.writeheader()
        writer.writerows(all_game_stats)

def count_possible_endings(all_game_stats, name):
    wins = 0
    draws = 0
    losses = 0

    for game_stats in all_game_stats:
        if name not in (game_stats["agent_1"], game_stats["agent_2"]): continue

        if game_stats["winner"] == 0: draws += 1
        elif game_stats["winner_name"] == name: wins += 1
        else: losses += 1

        return wins, draws, losses

def score(wins, draws, losses):
    games = wins + draws + losses
    return (wins + 0.5 * draws) / games

def mean_thinking_time(all_game_stats, name):
    total = 0.0
    moves = 0

    for game_stats in all_game_stats:
        if game_stats["agent_1"] == name:
            total += game_stats["agent_1_thinking"]
            moves += game_stats["agent_1_moves"]

        if game_stats["agent_2"] == name:
            total += game_stats["agent_2_thinking"]
            moves += game_stats["agent_2_moves"]

    return total / moves