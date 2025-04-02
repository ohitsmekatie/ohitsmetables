from flask import Blueprint, render_template, jsonify, request
from .sheets import get_random_encounter, get_random_lore

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

@main.route("/quests")
def quests():
    return render_template("quests.html")

@main.route("/random-encounters")
def random_encounters():
    return render_template("random_encounters.html")

@main.route("/random-encounter")
def random_encounter():
    biome = request.args.get("biome")
    difficulty = request.args.get("difficulty")

    try:
        encounter = get_random_encounter(biome=biome, difficulty=difficulty)
        return jsonify({"encounter": encounter})
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
