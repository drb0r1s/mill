import random as r

from mcts import MCTS

class RandomAgent:
    __slots__ = ("name", "random")

    def __init__(self, name = "Random", seed = None):
        self.name = name
        self.random = r.Random(seed)

    def play(self, model, player):
        moves = model.legal_moves(player)
        return moves[self.random.randrange(len(moves))]

    def report(self):
        return {}

class MCTSAgent:
    __slots__ = ("name", "random", "iterations", "c", "epsilon", "mcts", "_decisions", "_mistakes", "_searches", "_depth_sum", "_fraction_sum")
    
    def __init__(self, name = "MCTS", seed = None, iterations = 200, c = 2, epsilon = 0.0):
        self.name = name
        self.random = r.Random(seed)
        self.iterations = iterations
        self.c = c
        self.epsilon = epsilon
        self.mcts = MCTS(iterations = iterations, c = c, random = self.random)

        self._decisions = 0
        self._mistakes = 0
        self._searches = 0
        self._depth_sum = 0
        self._fraction_sum = 0.0

    def play(self, model, player, turns):
        self._decisions += 1

        # Mistake move
        if self.epsilon > 0 and self.random.random() < self.epsilon:
            self._mistakes += 1

            moves = model.legal_moves(player)
            return moves[self.random.randrange(len(moves))]

        # MCTS move
        move = self.mcts.search(model, player, turns)

        self._searches += 1
        self._depth_sum += self.mcts.last_stats["max_depth"]
        self._fraction_sum += self.mcts.last_stats["best_visit_fraction"]

        return move

    def report(self):
        searches = max(1, self._searches)

        return {
            "mistakes": self._mistakes,
            "mean_tree_depth": self._depth_sum / searches,
            "mean_best_visit_fraction": self._fraction_sum / searches
        }

def build_agent(props, seed):
    props = dict(props) # A copy of properties, to avoid editing the passed ones.

    agent = props.pop("agent")
    name = props.pop("name")

    if agent == "random": return RandomAgent(seed=seed, name=name)
    if agent == "mcts": return MCTSAgent(seed=seed, name=name, **props) # Spreading all other properties.