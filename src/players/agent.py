import time

from famnit_gym.envs import mill

def agent_play(agent1, agent2, render_mode = None):
    agents = { "player_1": agent1, "player_2": agent2 }

    env = mill.env(render_mode = render_mode)
    env.reset()

    thinking = { "player_1": 0.0, "player_2": 0.0 }
    moves = { "player_1": 0, "player_2": 0 }
    captures = { "player_1": 0, "player_2": 0 }

    turns = 0

    for name in env.agent_iter():
        _, _, termination, truncation, info = env.last()

        if termination or truncation: break

        player = 1
        if name == "player_2": player = 2

        # info["move"] - 1 in order to get total number of rounds (round = 2turns).
        # We have to subtract 1 from info["move"], because "move" starts from 1.
        # player - 1 represents the current round being played (its progress).
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
    elif final_model.get_phase(2) == "lost": winner = 1
    else: winner = 0

    return {
        "winner": winner,
        "turns": turns,
        "player_1_pieces": final_model.count_pieces(1),
        "player_2_pieces": final_model.count_pieces(2),
        "player_1_thinking": thinking["player_1"],
        "player_2_thinking": thinking["player_2"],
        "player_1_moves": moves["player_1"],
        "player_2_moves": moves["player_2"],
        "player_1_captures": captures["player_1"],
        "player_2_captures": captures["player_2"],
    }