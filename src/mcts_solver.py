import random
import copy
import time
import math
from config import COLORS, NATIONALITIES, DRINKS, PETS, HOBBIES, HOUSE_COUNT
from state import ZebraState
from llm_utils import query_gemini

# -------------------------------
# Node Class for MCTS
# -------------------------------
class MCTSNode:
    def __init__(self, state: ZebraState, parent=None, move=None):
        self.state = state                # Current puzzle state
        self.parent = parent              # Parent node
        self.children = []                # List of child nodes
        self.move = move                  # Move leading to this state
        self.visits = 0                   # Times this node was visited
        self.reward = 0                   # Accumulated reward

    def is_fully_expanded(self):
        """Check if all possible moves have been tried."""
        return len(self.children) == len(generate_possible_moves(self.state))

    def best_child(self, c_param=1.4):
        """Use UCT (Upper Confidence Bound) to select the best child."""
        choices = []
        for child in self.children:
            uct = (child.reward / (child.visits + 1e-6)) + c_param * math.sqrt(
                math.log(self.visits + 1) / (child.visits + 1e-6)
            )
            choices.append((uct, child))
        return max(choices, key=lambda x: x[0])[1]

# -------------------------------
# Generate Possible Moves
# -------------------------------
def generate_possible_moves(state: ZebraState):
    """
    Generate all possible valid attribute assignments for the next empty slot.
    Each move is a tuple: (house_index, attribute_type, value)
    """
    moves = []
    attributes = {
        "color": COLORS,
        "nationality": NATIONALITIES,
        "drink": DRINKS,
        "pet": PETS,
        "hobby": HOBBIES
    }

    for i in range(HOUSE_COUNT):
        for attr, values in attributes.items():
            if attr not in state.houses[i]:
                for val in values:
                    # Avoid duplicate usage
                    if val not in [h.get(attr) for h in state.houses]:
                        moves.append((i, attr, val))
                return moves  # Expand one attribute at a time
    return moves

# -------------------------------
# Apply a Move
# -------------------------------
def apply_move(state: ZebraState, move):
    new_state = state.clone()
    house_index, attr, value = move
    new_state.houses[house_index][attr] = value
    return new_state

# -------------------------------
# MCTS Solver
# -------------------------------
class MCTSSolver:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, initial_state):
        root = MCTSNode(initial_state)

        for _ in range(self.iterations):
            node = self.select(root)
            expanded_node = self.expand(node)
            reward, completed_state = self.simulate(expanded_node.state)
            expanded_node.state = completed_state  # Update state with simulation result
            self.backpropagate(expanded_node, reward)

        return self.get_best_solution(root)

    def select(self, node):
        """Select a leaf node using UCT."""
        while node.children and node.is_fully_expanded():
            node = node.best_child()
        return node

    def expand(self, node):
        """Expand tree by adding a new child node from unexplored moves."""
        possible_moves = generate_possible_moves(node.state)
        tried_moves = [child.move for child in node.children]
        untried_moves = [m for m in possible_moves if m not in tried_moves]

        if not untried_moves:
            return node

        move = random.choice(untried_moves)
        new_state = apply_move(node.state, move)
        child_node = MCTSNode(new_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def simulate(self, state):
        """
        Simulate a complete solution using Gemini mock and fallback logic.
        Reward based on how many constraints are satisfied.
        """
        temp_state = state.clone()

        # Ask Gemini to suggest completions for the remaining slots
        suggestion = query_gemini(temp_state.houses)

        # Apply Gemini's suggestion
        for i, attrs in enumerate(suggestion):
            for k, v in attrs.items():
                temp_state.houses[i][k] = v

        # Compute partial reward
        reward = self.evaluate_state(temp_state)
        return reward, temp_state

    def evaluate_state(self, state):
        """
        Reward system for Zebra puzzle:
        +1 for each satisfied constraint (out of 15).
        """
        score = 0
        houses = state.houses

        def find(attr, value):
            for i, h in enumerate(houses):
                if h.get(attr) == value:
                    return i
            return -1

        # 1. Englishman -> red house
        if find("nationality", "englishman") == find("color", "red"): score += 1
        # 2. Spaniard -> dog
        if find("nationality", "spaniard") == find("pet", "dog"): score += 1
        # 3. Coffee -> green house
        if find("drink", "coffee") == find("color", "green"): score += 1
        # 4. Ukrainian -> tea
        if find("nationality", "ukrainian") == find("drink", "tea"): score += 1
        # 5. Green immediately to right of ivory
        if find("color", "green") == find("color", "ivory") + 1: score += 1
        # 6. Old Gold -> snails (we'll use "reading" as placeholder for cigars)
        if find("hobby", "reading") == find("pet", "snails"): score += 1
        # 7. Kools -> yellow house ("football" = Kools)
        if find("hobby", "football") == find("color", "yellow"): score += 1
        # 8. Milk -> middle house (index 2)
        if find("drink", "milk") == 2: score += 1
        # 9. Norwegian -> first house (index 0)
        if find("nationality", "norwegian") == 0: score += 1
        # 10. Chesterfields next to fox ("chess" = Chesterfields)
        if abs(find("hobby", "chess") - find("pet", "fox")) == 1: score += 1
        # 11. Kools next to horse ("football" next to horse)
        if abs(find("hobby", "football") - find("pet", "horse")) == 1: score += 1
        # 12. Lucky Strike -> orange juice ("dancing" = Lucky Strike)
        if find("hobby", "dancing") == find("drink", "orange juice"): score += 1
        # 13. Japanese -> Parliament ("painter" = Parliament)
        if find("nationality", "japanese") == find("hobby", "painter"): score += 1
        # 14. Norwegian next to blue house
        if abs(find("nationality", "norwegian") - find("color", "blue")) == 1: score += 1
        # 15. Water next to Chesterfields ("chess")
        if abs(find("drink", "water") - find("hobby", "chess")) == 1: score += 1

        return score / 15  # Normalize to [0,1]

    def backpropagate(self, node, reward):
        """Propagate simulation results up the tree."""
        while node:
            node.visits += 1
            node.reward += reward
            node = node.parent

    def get_best_solution(self, root):
        """Return the most filled solution with best reward score."""
        best_child = None
        best_score = -1

        for child in root.children:
            filled = sum(len(house) for house in child.state.houses)
            score = (child.reward / (child.visits + 1e-6)) + (filled / (HOUSE_COUNT * 5)) * 0.5
            if score > best_score:
                best_score = score
                best_child = child

        return best_child.state if best_child else None
