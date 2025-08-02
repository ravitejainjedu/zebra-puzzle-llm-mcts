import random
from mcts_solver import MCTSNode, generate_possible_moves, apply_move
from csp_solver import complete_with_csp
from state import ZebraState

class HybridMCTSSolver:
    def __init__(self, iterations=1000):
        self.iterations = iterations

    def search(self, initial_state):
        root = MCTSNode(initial_state)
        best_completed_state = None

        for _ in range(self.iterations):
            node = self.select(root)
            if node.state.is_valid():
                expanded_node = self.expand(node)

                # Hybrid part: simulate by completing with CSP
                completed_state, reward = self.simulate_with_csp(expanded_node.state)

                if reward > 0:
                    # Store completed state in the node
                    expanded_node.state = completed_state
                    best_completed_state = completed_state

                self.backpropagate(expanded_node, reward)

        return best_completed_state or root.state

    def select(self, node):
        while node.children and node.is_fully_expanded():
            node = node.best_child()
        return node

    def expand(self, node):
        possible_moves = generate_possible_moves(node.state)
        tried_moves = [child.move for child in node.children]
        untried_moves = [m for m in possible_moves if m not in tried_moves]

        if not untried_moves:
            return node

        move = random.choice(untried_moves)
        new_state = apply_move(node.state, move)

        if new_state.is_valid():
            child_node = MCTSNode(new_state, parent=node, move=move)
            node.children.append(child_node)
            return child_node

        return node

    def simulate_with_csp(self, partial_state):
        """
        Use CSP solver to complete partial state and return:
        - completed state (if valid)
        - reward (1 if valid solution, 0 otherwise)
        """
        # Convert ZebraState -> list of dicts
        partial_list = [dict(h) for h in partial_state.houses]

        # Call CSP solver
        completed_list = complete_with_csp(partial_list)

        # If CSP found solution, convert back to ZebraState
        if completed_list:
            completed_state = ZebraState(completed_list)
            if completed_state.is_valid():
                return completed_state, 1

        return partial_state, 0

    def backpropagate(self, node, reward):
        while node:
            node.visits += 1
            node.reward += reward
            node = node.parent
