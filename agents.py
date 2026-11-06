import random as r

from mcts import MCTS

class RandomAgent:
    __slots__ = ("name", "random")

    def __init__(self, name = "random", seed = None):
        self.name = name
        self.random = r.Random(seed)

    def play(self, model, player):
        moves = model.legal_moves(player)
        return moves[self.random.randrange(len(moves))]

    def report(self):
        return {}

class MCTSAgent:
    __slots__ = ("name", "random", "iterations", "c", "epsilon", "mcts")
    
    def __init__(self, name = "MCTS", seed = None, iterations = 200, c = 2, epsilon = 0.0):
        self.name = name
        self.random = r.Random(seed)
        self.iterations = iterations
        self.c = c
        self.epsilon = epsilon
        self.mcts = MCTS(iterations = iterations, c = c, random = self.random)