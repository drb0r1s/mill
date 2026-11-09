import math
import random as r

class Node:
    __slots__ = ("model", "current_player", "prev_player", "turns", "move", "parent", "children", "not_tried", "visits", "total_reward", "is_terminal", "depth")

    def __init__(self, model, current_player, turns, max_turns, random, move = None, parent = None):
        self.model = model
        self.current_player = current_player
        self.prev_player = 3 - current_player
        self.turns = turns
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0.0

        if parent is None: self.depth = 0
        else: self.depth = parent.depth + 1

        if model.game_over() or turns >= max_turns:
            self.not_tried = []
            self.is_terminal = True

        else:
            self.not_tried = model.legal_moves(current_player)
            random.shuffle(self.not_tried)

            self.is_terminal = len(self.not_tried) == 0

class MCTS:
    __slots__ = ("iterations", "c", "max_turns", "random", "last_stats")
    
    def __init__(self, iterations = 1000, c = math.sqrt(2), max_turns = 200, random = None):
        self.iterations = iterations
        self.c = c
        self.max_turns = max_turns

        if random is None: self.random = r.Random()
        else: self.random = random

        self.last_stats = {}

    def search(self, model, player, turn = 0):
        root = Node(model.clone(), player, turn, self.max_turns, self.random)

        if root.is_terminal: return None

        max_depth = 0

        for _ in range(self.iterations):
            node = root

            # 1. Selection
            while not node.is_terminal and not node.not_tried:
                node = self._select(node)

            # 2. Expansion
            if not node.is_terminal:
                node = self._expand(node)
                if node.depth > max_depth: max_depth = node.depth

            # 3. Simulation
            reward = self._playout(node, player)

            # 4. Backpropagation
            while node is not None:
                node.visits += 1

                if node.prev_player == player: node.total_reward += reward
                else: node.total_reward -= reward

                node = node.parent

        best_node = self._get_most_visited(root)

        self.last_stats = {
            "iterations": self.iterations,
            "max_depth": max_depth,
            "best_visit_fraction": best_node.visits / max(1, root.visits),
            "best_value": best_node.total_reward / best_node.visits,
            "root_children": len(root.children)
        }

        return best_node.move

    def _select(self, node):
        log_N = math.log(node.visits)
        c = self.c

        best_child = None
        best_value = -math.inf

        for child in node.children:
            value = child.total_reward / child.visits + c * math.sqrt(log_N / child.visits)

            if value > best_value:
                best_child = child
                best_value = value

        return best_child

    def _expand(self, node):
        move = node.not_tried.pop()

        model = node.model.clone()
        model.make_move(node.current_player, move)

        child = Node(model, 3 - node.current_player, node.turns + 1, self.max_turns, self.random, move = move, parent = node)
        node.children.append(child)

        return child

    def _playout(self, node, player):
        if node.is_terminal:
            return self._get_reward(node.model, player)

        model = node.model.clone()

        current_player = node.current_player
        turns = node.turns

        while not model.game_over() and turns < self.max_turns:
            moves = model.legal_moves(current_player)
            model.make_move(current_player, moves[self.random.randrange(len(moves))])

            current_player = 3 - current_player
            turns += 1

        return self._get_reward(model, player)

    def _get_reward(self, model, player):
        if model.get_phase(player) == "lost": return -1.0
        if model.get_phase(3 - player) == "lost": return 1.0

        return 0

    def _get_most_visited(self, root):
        most_visits = -math.inf

        for child in root.children:
            if(child.visits > most_visits): most_visits = child.visits

        most_visited_children = []

        for child in root.children:
            if(child.visits == most_visits): most_visited_children.append(child)

        return self.random.choice(most_visited_children)