from config import COLORS, NATIONALITIES, DRINKS, PETS, HOBBIES, HOUSE_COUNT

# ================================
# CSP SOLVER WITH PRUNING + MRV
# ================================

def is_valid_partial(solution):
    """
    Check partial solution against all Zebra puzzle constraints.
    This function prunes invalid states early.
    """
    for i, house in enumerate(solution):

        # Rule 2: Englishman in red house
        if house.get("nationality") == "englishman" and house.get("color") not in (None, "red"):
            return False
        if house.get("color") == "red" and house.get("nationality") not in (None, "englishman"):
            return False

        # Rule 3: Spaniard owns dog
        if house.get("nationality") == "spaniard" and house.get("pet") not in (None, "dog"):
            return False
        if house.get("pet") == "dog" and house.get("nationality") not in (None, "spaniard"):
            return False

        # Rule 4: Green house drinks coffee
        if house.get("color") == "green" and house.get("drink") not in (None, "coffee"):
            return False
        if house.get("drink") == "coffee" and house.get("color") not in (None, "green"):
            return False

        # Rule 5: Ukrainian drinks tea
        if house.get("nationality") == "ukrainian" and house.get("drink") not in (None, "tea"):
            return False
        if house.get("drink") == "tea" and house.get("nationality") not in (None, "ukrainian"):
            return False

        # Rule 7: Snail owner dances
        if house.get("pet") == "snails" and house.get("hobby") not in (None, "dancing"):
            return False
        if house.get("hobby") == "dancing" and house.get("pet") not in (None, "snails"):
            return False

        # Rule 8: Yellow house -> painter
        if house.get("color") == "yellow" and house.get("hobby") not in (None, "painter"):
            return False
        if house.get("hobby") == "painter" and house.get("color") not in (None, "yellow"):
            return False

        # Rule 9: Middle house drinks milk (house index 2)
        if i == 2 and house.get("drink") not in (None, "milk"):
            return False

        # Rule 10: Norwegian in first house (index 0)
        if i == 0 and house.get("nationality") not in (None, "norwegian"):
            return False

        # Rule 13: Football -> orange juice
        if house.get("hobby") == "football" and house.get("drink") not in (None, "orange juice"):
            return False
        if house.get("drink") == "orange juice" and house.get("hobby") not in (None, "football"):
            return False

        # Rule 14: Japanese -> chess
        if house.get("nationality") == "japanese" and house.get("hobby") not in (None, "chess"):
            return False
        if house.get("hobby") == "chess" and house.get("nationality") not in (None, "japanese"):
            return False

    # Rule 6: Green house right of ivory
    colors = [h.get("color") for h in solution]
    if "green" in colors and "ivory" in colors:
        green_idx = colors.index("green")
        ivory_idx = colors.index("ivory")
        if green_idx != ivory_idx + 1:
            return False

    # Rule 11: Reader next to fox owner
    for i, house in enumerate(solution):
        if house.get("hobby") == "reading":
            if not ((i > 0 and solution[i-1].get("pet") in (None, "fox")) or
                    (i < 4 and solution[i+1].get("pet") in (None, "fox"))):
                return False

    # Rule 12: Painter next to horse owner
    for i, house in enumerate(solution):
        if house.get("hobby") == "painter":
            if not ((i > 0 and solution[i-1].get("pet") in (None, "horse")) or
                    (i < 4 and solution[i+1].get("pet") in (None, "horse"))):
                return False

    # Rule 15: Norwegian next to blue house
    for i, house in enumerate(solution):
        if house.get("nationality") == "norwegian":
            if not ((i > 0 and solution[i-1].get("color") in (None, "blue")) or
                    (i < 4 and solution[i+1].get("color") in (None, "blue"))):
                return False

    return True


def select_unassigned_variable(solution, domains):
    """Select house and attribute with Minimum Remaining Values (MRV)."""
    min_choices = float("inf")
    choice = None

    for house_idx in range(HOUSE_COUNT):
        for attr in ["color", "nationality", "drink", "pet", "hobby"]:
            if attr not in solution[house_idx]:
                remaining = len(domains[house_idx][attr])
                if remaining < min_choices:
                    min_choices = remaining
                    choice = (house_idx, attr)
    return choice


def backtrack(solution, domains):
    """Recursive backtracking with forward checking."""
    # Check if solution is complete
    if all(len(house) == 5 for house in solution):
        return solution

    var = select_unassigned_variable(solution, domains)
    if not var:
        return None
    house_idx, attr = var

    for value in list(domains[house_idx][attr]):
        # Create new state
        new_solution = [dict(h) for h in solution]
        new_solution[house_idx][attr] = value

        # Clone domains
        new_domains = [{k: v.copy() for k, v in row.items()} for row in domains]

        # Forward checking: remove value from other houses' domains
        for i in range(HOUSE_COUNT):
            if i != house_idx and value in new_domains[i][attr]:
                new_domains[i][attr].remove(value)

        if is_valid_partial(new_solution):
            result = backtrack(new_solution, new_domains)
            if result:
                return result

    return None


def solve_csp():
    """Main CSP solver entry point for solving from scratch."""
    solution = [{} for _ in range(HOUSE_COUNT)]
    domains = [{ "color": set(COLORS), "nationality": set(NATIONALITIES),
                 "drink": set(DRINKS), "pet": set(PETS), "hobby": set(HOBBIES)}
               for _ in range(HOUSE_COUNT)]
    return backtrack(solution, domains)


def complete_with_csp(partial_solution):
    """
    Takes a partially filled state and completes it using CSP.
    Useful for MCTS rollouts or hybrid solving.
    """
    # Start with partial solution
    solution = [dict(h) for h in partial_solution]

    # Initialize domains and remove used values
    domains = []
    for i in range(HOUSE_COUNT):
        domains.append({
            "color": set(COLORS) - {solution[j].get("color") for j in range(HOUSE_COUNT) if j != i and "color" in solution[j]},
            "nationality": set(NATIONALITIES) - {solution[j].get("nationality") for j in range(HOUSE_COUNT) if j != i and "nationality" in solution[j]},
            "drink": set(DRINKS) - {solution[j].get("drink") for j in range(HOUSE_COUNT) if j != i and "drink" in solution[j]},
            "pet": set(PETS) - {solution[j].get("pet") for j in range(HOUSE_COUNT) if j != i and "pet" in solution[j]},
            "hobby": set(HOBBIES) - {solution[j].get("hobby") for j in range(HOUSE_COUNT) if j != i and "hobby" in solution[j]},
        })

    return backtrack(solution, domains)
