import time
import csv
import matplotlib.pyplot as plt
import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from state import ZebraState
from mcts_solver import MCTSSolver
from csp_solver import solve_csp
from hybrid_solver import HybridMCTSSolver

# ===============================
# Helper functions
# ===============================

def test_mcts_llm(runs=5):
    success = 0
    total_time = 0
    solver = MCTSSolver(iterations=50)

    for _ in range(runs):
        state = ZebraState()
        start = time.time()
        solution = solver.search(state)
        end = time.time()

        total_time += (end - start)
        if solution and solution.is_valid():
            success += 1

    return total_time / runs, (success / runs) * 100


def test_csp(runs=5):
    success = 0
    total_time = 0

    for _ in range(runs):
        start = time.time()
        result = solve_csp()
        end = time.time()

        total_time += (end - start)
        if result:
            success += 1

    return total_time / runs, (success / runs) * 100


def test_hybrid(runs=5):
    success = 0
    total_time = 0
    solver = HybridMCTSSolver(iterations=50)

    for _ in range(runs):
        state = ZebraState()
        start = time.time()
        solution = solver.search(state)
        end = time.time()

        total_time += (end - start)
        if solution and solution.is_valid():
            success += 1

    return total_time / runs, (success / runs) * 100


# ===============================
# Main benchmarking process
# ===============================
def main():
    runs = 5  # number of times each solver is tested

    print("🔍 Benchmarking MCTS + LLM...")
    mcts_time, mcts_success = test_mcts_llm(runs)

    print("🔍 Benchmarking CSP solver...")
    csp_time, csp_success = test_csp(runs)

    print("🔍 Benchmarking Hybrid solver...")
    hybrid_time, hybrid_success = test_hybrid(runs)

    # Save results
    results = [
        ["Algorithm", "Avg_Time(s)", "Success_Rate(%)"],
        ["MCTS + LLM", mcts_time, mcts_success],
        ["CSP Solver", csp_time, csp_success],
        ["Hybrid MCTS + CSP", hybrid_time, hybrid_success]
    ]

    with open("benchmark_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)

    print("\n✅ Benchmark results saved to 'benchmark_results.csv'\n")

    # ==========================
    # Generate chart
    # ==========================
    algorithms = [r[0] for r in results[1:]]
    times = [r[1] for r in results[1:]]
    success = [r[2] for r in results[1:]]

    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Algorithms')
    ax1.set_ylabel('Time (s)', color=color)
    ax1.bar(algorithms, times, color=color, alpha=0.6)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Success Rate (%)', color=color)
    ax2.plot(algorithms, success, color=color, marker='o', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Zebra Puzzle Solver Comparison")
    plt.tight_layout()
    plt.savefig("benchmark_chart.png")
    plt.show()

    print("✅ Chart saved as 'benchmark_chart.png'")


if __name__ == "__main__":
    main()
