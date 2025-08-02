import os
import json
import random
from config import COLORS, NATIONALITIES, DRINKS, PETS, HOBBIES, HOUSE_COUNT
from utils import setup_gemini

# Avoid logging multiple fallback messages
gemini_failed_once = False

# -------------------------------
# Gemini API Query with Retry
# -------------------------------
def query_gemini_api(current_state, retries=2):
    """
    Query Gemini API safely, enforcing JSON-only output.
    Retries up to 'retries' times if response is empty or invalid.
    Returns: List of 5 dictionaries or None.
    """
    global gemini_failed_once

    prompt = (
        "You are solving the Zebra Puzzle logically. "
        "Given the current partial state of 5 houses:\n"
        f"{current_state}\n\n"
        "Fill in ALL missing attributes following these rules:\n"
        "1. The Englishman lives in the red house.\n"
        "2. The Spaniard owns the dog.\n"
        "3. The person in the green house drinks coffee.\n"
        "4. The Ukrainian drinks tea.\n"
        "5. The green house is immediately to the right of the ivory house.\n"
        "6. The snail owner likes to go dancing.\n"
        "7. The person in the yellow house is a painter.\n"
        "8. The person in the middle house drinks milk.\n"
        "9. The Norwegian lives in the first house.\n"
        "10. The person who enjoys reading lives next to the person with the fox.\n"
        "11. The painter's house is next to the house with the horse.\n"
        "12. The person who plays football drinks orange juice.\n"
        "13. The Japanese person plays chess.\n"
        "14. The Norwegian lives next to the blue house.\n\n"
        "Return ONLY valid JSON in this exact format:\n"
        "[\n"
        "  {\"color\": \"\", \"nationality\": \"\", \"drink\": \"\", \"pet\": \"\", \"hobby\": \"\"},\n"
        "  {...},\n"
        "  {...},\n"
        "  {...},\n"
        "  {...}\n"
        "]\n"
        "No explanations, no extra text, only JSON."
    )

    for attempt in range(retries + 1):
        try:
            model = setup_gemini()
            response = model.generate_content(prompt, generation_config={"max_output_tokens": 512, "response_mime_type": "application/json"})
            text = (response.text or "").strip()

            # ✅ Handle empty response
            if not text:
                continue

            # ✅ Extract JSON if wrapped in code blocks
            if "```" in text:
                parts = text.split("```")
                for part in parts:
                    if part.strip().startswith("["):
                        text = part.strip()
                        break

            # ✅ Parse JSON
            suggestion = json.loads(text)
            if isinstance(suggestion, list) and len(suggestion) == 5:
                return suggestion

        except json.JSONDecodeError:
            continue
        except Exception:
            continue

    if not gemini_failed_once:
        print("⚠️ Gemini failed to provide valid JSON after retries, fallback to mock.")
        gemini_failed_once = True
    return None


# -------------------------------
# Mock LLM Fallback
# -------------------------------
def query_mock_llm(current_state):
    """Fallback: deterministic filler for missing attributes."""
    suggestion = [dict(house) for house in current_state]

    used_colors = {h.get("color") for h in suggestion if "color" in h}
    used_nationalities = {h.get("nationality") for h in suggestion if "nationality" in h}
    used_drinks = {h.get("drink") for h in suggestion if "drink" in h}
    used_pets = {h.get("pet") for h in suggestion if "pet" in h}
    used_hobbies = {h.get("hobby") for h in suggestion if "hobby" in h}

    for i in range(HOUSE_COUNT):
        house = suggestion[i]
        if "color" not in house:
            available = [c for c in COLORS if c not in used_colors]
            if available:
                choice = random.choice(available)
                house["color"] = choice
                used_colors.add(choice)
        if "nationality" not in house:
            available = [n for n in NATIONALITIES if n not in used_nationalities]
            if available:
                choice = random.choice(available)
                house["nationality"] = choice
                used_nationalities.add(choice)
        if "drink" not in house:
            available = [d for d in DRINKS if d not in used_drinks]
            if available:
                choice = random.choice(available)
                house["drink"] = choice
                used_drinks.add(choice)
        if "pet" not in house:
            available = [p for p in PETS if p not in used_pets]
            if available:
                choice = random.choice(available)
                house["pet"] = choice
                used_pets.add(choice)
        if "hobby" not in house:
            available = [h for h in HOBBIES if h not in used_hobbies]
            if available:
                choice = random.choice(available)
                house["hobby"] = choice
                used_hobbies.add(choice)
    return suggestion


# -------------------------------
# Unified Query
# -------------------------------
def query_gemini(current_state):
    """
    Use Gemini API occasionally to avoid quota errors, fallback to mock if needed.
    """
    if random.random() < 0.05:  # 5% of calls use Gemini
        result = query_gemini_api(current_state, retries=2)
        if result:
            return result

    return query_mock_llm(current_state)
