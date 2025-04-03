from flask import Blueprint, render_template, jsonify, request

from .sheets import (
    get_random_encounter,
    get_random_lore,
    get_flavor_text,
    get_random_character,
    get_random_food,
    get_random_landmark
)

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("landing.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/characters")
def characters():
    return render_template("characters.html")

@main.route("/random-encounters")
def random_encounters():
    return render_template("random_encounters.html")

@main.route("/random-encounter")
def random_encounter():
    biome = request.args.get("biome")
    difficulty = request.args.get("difficulty")

    try:
        encounter = get_random_encounter(biome=biome, difficulty=difficulty)
        flavor = get_flavor_text()
        return jsonify({
            "encounter": encounter,
            "flavor": flavor
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@main.route("/lore")
def lore():
    try:
        lore_entries = get_random_lore()
        return jsonify(lore_entries)
    except Exception as e:
        print("Error loading lore:", e)
        return jsonify([]), 500

@main.route("/character")
def character():
    try:
        from .sheets import get_random_character
        character = get_random_character()
        return jsonify(character)
    except Exception as e:
        print("Error loading character:", e)
        return jsonify({"error": str(e)}), 500

@main.route("/food")
def food():
    return render_template("food.html")

@main.route("/food-item")
def food_item():
    try:
        include_weird = request.args.get("weird") == "true"
        include_magical = request.args.get("magical") == "true"

        item = get_random_food(include_weird, include_magical)
        return jsonify(item)
    except Exception as e:
        print("Error loading food:", e)
        return jsonify({"error": str(e)}), 500

@main.route("/landmarks")
def landmarks():
    return render_template("landmarks.html")

@main.route("/landmark")
def landmark():
    biome = request.args.get("biome")
    include_rumor = request.args.get("rumor") == "true"

    try:
        result = get_random_landmark(biome)
        response = {"landmark": result}

        if include_rumor:
            from .sheets import get_random_rumor
            rumor = get_random_rumor()
            if rumor:
                response["rumor"] = rumor

        return jsonify(response)
    except Exception as e:
        print("Error fetching landmark:", e)
        return jsonify({"error": str(e)}), 500
