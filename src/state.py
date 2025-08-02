# src/state.py
from config import HOUSE_COUNT

class ZebraState:
    def __init__(self, houses=None):
        if houses is None:
            self.houses = [dict() for _ in range(HOUSE_COUNT)]
        else:
            self.houses = houses

    def clone(self):
        """Create a deep copy of the state."""
        new_state = ZebraState()
        new_state.houses = [h.copy() for h in self.houses]
        return new_state

    def get_neighbor_indices(self, index):
        """Return the valid neighbor indices of a given house index."""
        neighbors = []
        if index > 0:
            neighbors.append(index - 1)
        if index < HOUSE_COUNT - 1:
            neighbors.append(index + 1)
        return neighbors

    def is_valid(self):
        """Check all known Zebra Puzzle constraints dynamically."""
        houses = self.houses

        # 2. The Englishman lives in the red house
        for h in houses:
            if h.get("nationality") == "englishman" and h.get("color") not in (None, "red"):
                return False
            if h.get("color") == "red" and h.get("nationality") not in (None, "englishman"):
                return False

        # 3. The Spaniard owns the dog
        for h in houses:
            if h.get("nationality") == "spaniard" and h.get("pet") not in (None, "dog"):
                return False
            if h.get("pet") == "dog" and h.get("nationality") not in (None, "spaniard"):
                return False

        # 4. The person in the green house drinks coffee
        for h in houses:
            if h.get("color") == "green" and h.get("drink") not in (None, "coffee"):
                return False
            if h.get("drink") == "coffee" and h.get("color") not in (None, "green"):
                return False

        # 5. The Ukrainian drinks tea
        for h in houses:
            if h.get("nationality") == "ukrainian" and h.get("drink") not in (None, "tea"):
                return False
            if h.get("drink") == "tea" and h.get("nationality") not in (None, "ukrainian"):
                return False

        # 6. The green house is immediately to the right of the ivory house
        for i, h in enumerate(houses):
            if h.get("color") == "green":
                if i == 0:
                    return False
                left = houses[i-1].get("color")
                if left not in (None, "ivory"):
                    return False
            if h.get("color") == "ivory":
                if i == HOUSE_COUNT-1:
                    return False
                right = houses[i+1].get("color")
                if right not in (None, "green"):
                    return False

        # 7. The snail owner likes to go dancing
        for h in houses:
            if h.get("pet") == "snails" and h.get("hobby") not in (None, "dancing"):
                return False
            if h.get("hobby") == "dancing" and h.get("pet") not in (None, "snails"):
                return False

        # 8. The person in the yellow house is a painter
        for h in houses:
            if h.get("color") == "yellow" and h.get("hobby") not in (None, "painter"):
                return False
            if h.get("hobby") == "painter" and h.get("color") not in (None, "yellow"):
                return False

        # 9. The person in the middle house drinks milk
        mid = houses[2].get("drink")
        if mid not in (None, "milk"):
            return False

        # 10. The Norwegian lives in the first house
        first = houses[0].get("nationality")
        if first not in (None, "norwegian"):
            return False

        # 11. The person who enjoys reading lives next to the person with the fox
        for i, h in enumerate(houses):
            if h.get("hobby") == "reading":
                if not any(houses[n].get("pet") in (None, "fox") for n in self.get_neighbor_indices(i)):
                    return False
            if h.get("pet") == "fox":
                if not any(houses[n].get("hobby") in (None, "reading") for n in self.get_neighbor_indices(i)):
                    return False

        # 12. The painter's house is next to the house with the horse
        for i, h in enumerate(houses):
            if h.get("hobby") == "painter":
                if not any(houses[n].get("pet") in (None, "horse") for n in self.get_neighbor_indices(i)):
                    return False
            if h.get("pet") == "horse":
                if not any(houses[n].get("hobby") in (None, "painter") for n in self.get_neighbor_indices(i)):
                    return False

        # 13. The person who plays football drinks orange juice
        for h in houses:
            if h.get("hobby") == "football" and h.get("drink") not in (None, "orange juice"):
                return False
            if h.get("drink") == "orange juice" and h.get("hobby") not in (None, "football"):
                return False

        # 14. The Japanese person plays chess
        for h in houses:
            if h.get("nationality") == "japanese" and h.get("hobby") not in (None, "chess"):
                return False
            if h.get("hobby") == "chess" and h.get("nationality") not in (None, "japanese"):
                return False

        # 15. The Norwegian lives next to the blue house
        for i, h in enumerate(houses):
            if h.get("nationality") == "norwegian":
                if not any(houses[n].get("color") in (None, "blue") for n in self.get_neighbor_indices(i)):
                    return False

        return True
