DIFFICULTIES = {
    "peaceful": { "agent": "random" },
    "easy": { "agent": "mcts", "iterations": 15, "epsilon": 0.30 },
    "medium": { "agent": "mcts", "iterations": 150, "epsilon": 0.15 },
    "hard": { "agent": "mcts", "iterations": 500, "epsilon": 0.10 },
    "insanity": { "agent": "mcts", "iterations": 1000, "epsilon": 0.0 },
}