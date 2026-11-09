import os
import csv
import argparse
import time

from famnit_gym.envs import mill
from famnit_gym.wrappers.mill import UserInteraction

from agents import build_agent

from data.difficulties import DIFFICULTIES
from data.colors import RED, GREEN, YELLOW

def human_play(env, info):
    legal_move_tuples = []    

    for legal_move in info["legal_moves"]:
        move_tuple = tuple(prop for prop in legal_move)
        legal_move_tuples.append(move_tuple)

    is_placing = all(src == 0 for src, _, _, in legal_move_tuples)
    sources = sorted({ src for src, _, _ in legal_move_tuples })

    stage = "dst"
    if not is_placing: stage = "src"

    src = 0
    if not is_placing: src = None

    dst = None

    def repaint():
        env.clear_markings()

        if stage == "src":
            for source in sources: env.mark_position(source, YELLOW)

        elif stage == "dst":
            if not is_placing: env.mark_position(src, YELLOW)

            for current_src, current_dst, _ in legal_move_tuples:
                if current_src == src: env.mark_position(current_dst, GREEN)
            
        else:
            for current_src, current_dst, current_capture in legal_move_tuples:
                if current_src == src and current_dst == dst: env.mark_position(current_capture, RED)

    repaint()

    while True:
        interaction = env.interact()

        if interaction["type"] == "quit": return None

        if interaction["type"] == "key_press":
            if interaction["key"] == "escape": return None
            continue

        if interaction["type"] != "mouse_click" or interaction["position"] == 0: continue

        position = interaction["position"]

        if stage == "src":
            if position in sources:
                src = position
                stage = "dst"

        elif stage == "dst":
            if not is_placing and position == src:
                src = None
                stage = "src"

            elif not is_placing and position in sources:
                src = position

            else:
                captures = []

                for current_src, current_dst, current_capture in legal_move_tuples:
                    if current_src == src and current_dst == position: captures.append(current_capture)

                if captures:
                    dst = position

                    if captures == [0]:
                        env.clear_markings()
                        return [src, dst, 0]

                    stage = "capture"

        else:
            if (src, dst, position) in legal_move_tuples:
                env.clear_markings()
                return [src, dst, position]

        repaint()

def log_result(path, row):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    new_file = not os.path.exists(path)

    with open(path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(row.keys()))

        if new_file: writer.writeheader()
        writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Mill: Human vs AI")

    parser.add_argument("--difficulty", choices = list(DIFFICULTIES), default = "medium")
    parser.add_argument("--side", type = int, choices=[1, 2], default = 1)
    parser.add_argument("--seed", type = int, default = None)
    parser.add_argument("--log", default = "results/human-vs-ai.csv")

    args = parser.parse_args()

    agent = build_agent(dict(DIFFICULTIES[args.difficulty]), args.seed)

    env = UserInteraction(mill.env(render_mode = "human"))
    env.reset()

    outcome = None # ["human", "agent", "draw"]
    turns = 0

    agent_time = 0.0
    agent_moves = 0

    human_name = f"player_{args.side}"

    for name in env.agent_iter():
        _, _, termination, truncation, info = env.last()

        if termination:
            # The name has lost.
            if name == human_name: outcome = "agent"
            else: outcome = "human"

            break

        if truncation:
            if info.get("move") > 100: outcome = "draw"
            break

        if name == human_name:
            move = human_play(env, info)

            if move is None:
                print("Game terminated.")
                break

        else:
            agent_side = 3 - args.side
            
            # info["move"] - 1 in order to get total number of rounds (round = 2turns).
            # We have to subtract 1 from info["move"], because "move" starts from 1.
            # agent_side - 1 represents the current round being played (its progress).
            turns = 2 * (info["move"] - 1) + agent_side - 1

            model = mill.transition_model(env.unwrapped)
            start = time.perf_counter()

            move = agent.play(model, agent_side, turns)

            agent_time += time.perf_counter() - start
            agent_moves += 1

        env.step(move)

        turns += 1

    if outcome is not None:
        message = {
            "human": "You won!",
            "agent": "The AI won.",
            "draw": "Draw, game was too long."
        }

        print(message[outcome])

        log_result(args.log, {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty": args.difficulty,
            "human_side": args.side,
            "agent_side": 3 - args.side,
            "outcome": outcome,
            "turns": turns,
            "agent_mean_thinking_time": round(agent_time / agent_moves, 3) if agent_moves else ""
        })

        print("Press any key in the window to exit.")

        while True:
            interaction = env.interact()

            if interaction["type"] in ("quit", "key_press"):
                break

    env.close()

if __name__ == "__main__": main()