import os
import time
import sys
import multiprocessing

from src.classes.agents import build_agent
from src.players.agent import agent_play

def play_task(task):
    agent1 = build_agent(task["player_1_props"], f"player_1_seed:{task['seed']}")
    agent2 = build_agent(task["player_2_props"], f"player_2_seed:{task['seed']}")

    if agent1.name == agent2.name:
        agent1.name = f"{agent1.name}_1"
        agent2.name = f"{agent2.name}_2"

    result = agent_play(agent1, agent2)

    game_stats = {
        "id": task.get("id"),
        "game": task["game"],
        "seed": task["seed"],
        "player_1": agent1.name,
        "player_2": agent2.name,
        "winner_name": None
    }

    game_stats.update(result)

    if result["winner"] == 1: game_stats["winner_name"] = agent1.name
    elif result["winner"] == 2: game_stats["winner_name"] = agent2.name
    else: game_stats["winner_name"] = "neither"

    for id, agent in (("player_1", agent1), ("player_2", agent2)):
        report = agent.report()

        game_stats[f"{id}_mistakes"] = report.get("mistakes")
        game_stats[f"{id}_mean_tree_depth"] = report.get("mean_tree_depth")
        game_stats[f"{id}_mean_best_visit_fraction"] = report.get("mean_best_visit_fraction")

    return game_stats

def run_tasks(tasks, workers = None, description = ""):
    workers = workers or os.cpu_count() or 1

    all_game_stats = []
    total_tasks_amunt = len(tasks)

    start = time.perf_counter()

    def progress(finished_tasks_amount):
        elapsed = time.perf_counter() - start
        print(f"{description} {finished_tasks_amount}/{total_tasks_amunt} games, {elapsed:.0f}s", file = sys.stderr, flush = True)

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