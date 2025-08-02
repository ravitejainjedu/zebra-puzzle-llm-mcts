import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hybrid_solver import HybridMCTSSolver
from state import ZebraState

if __name__ == "__main__":
    print("🔹 Running Hybrid MCTS + CSP Solver...")

    solver = HybridMCTSSolver(iterations=2000)  # You can increase iterations for better results
    initial_state = ZebraState()
    solution = solver.search(initial_state)

    print("\n=== HYBRID SOLUTION FOUND ===")
    for i, house in enumerate(solution.houses, 1):
        print(f"\nHouse {i}:")
        for k, v in house.items():
            print(f"  {k}: {v}")

    # Check if final solution is valid
    print("\nSolution valid?", solution.is_valid())
