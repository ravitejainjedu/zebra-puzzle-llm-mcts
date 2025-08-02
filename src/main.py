from state import ZebraState
from mcts_solver import MCTSSolver

def print_solution(state):
    """Nicely format and print the solved Zebra Puzzle state."""
    print("\n=== BEST SOLUTION FOUND ===\n")
    for i, house in enumerate(state.houses):
        print(f"House {i+1}:")
        for attr, val in house.items():
            print(f"  {attr}: {val}")
        print("")

def extract_answers(state):
    """Find the residents for the two Zebra Puzzle questions."""
    water_drinker = None
    zebra_owner = None

    for house in state.houses:
        if house.get("drink") == "water":
            water_drinker = house.get("nationality")
        if house.get("pet") == "zebra":
            zebra_owner = house.get("nationality")

    print("=== FINAL ANSWERS ===")
    print(f"1️⃣ The resident who drinks water is: {water_drinker}")
    print(f"2️⃣ The owner of the zebra is: {zebra_owner}\n")

def main():
    # Step 1: Initialize an empty Zebra puzzle state
    initial_state = ZebraState()
    
    # Step 2: Initialize MCTS solver
    solver = MCTSSolver(iterations=50)  # Start small for testing, increase later
    
    # Step 3: Search for solution
    print("🔍 Running MCTS to solve Zebra Puzzle...\n")
    best_solution = solver.search(initial_state)
    
    # Step 4: Print result and answers
    if best_solution:
        print_solution(best_solution)
        extract_answers(best_solution)
    else:
        print("❌ No solution found. Try increasing iterations or adjusting prompts.")

if __name__ == "__main__":
    main()
