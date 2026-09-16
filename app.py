from flask import Flask, render_template, request, jsonify, session

import game


app = Flask(__name__)
app.secret_key = "change-this-secret-key"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# GAME STATE
# ============================================================

@app.route("/api/state")
def get_state():

    current_scene = game.scenes.get(
        game.current_scene,
        {}
    )

    scene_npcs = []

    for npc_name in current_scene.get("npcs", []):
        if npc_name in game.npcs:
            scene_npcs.append(game.npcs[npc_name])

    return jsonify({
        "stats": game.stats,
        "inventory": game.inventory,
        "current_scene": game.current_scene,
        "scene": current_scene,
        "npcs": scene_npcs
    })


# ============================================================
# CHARACTER CREATION
# ============================================================

@app.route("/api/create-character", methods=["POST"])
def create_character():

    data = request.json or {}

    name = data.get("name", "").strip()
    character_class = data.get("class", "").strip()
    backstory = data.get("backstory", "").strip()

    if not name:
        return jsonify({
            "error": "Character name is required."
        }), 400

    if not character_class:
        return jsonify({
            "error": "Character class is required."
        }), 400

    try:
        strength = int(data.get("strength", 10))
        dexterity = int(data.get("dexterity", 10))
        intelligence = int(data.get("intelligence", 10))
    except ValueError:
        return jsonify({
            "error": "Stats must be numbers."
        }), 400

    if strength + dexterity + intelligence != 30:
        return jsonify({
            "error": "Strength, Dexterity and Intelligence must total 30."
        }), 400

    if not all(
        1 <= value <= 20
        for value in [
            strength,
            dexterity,
            intelligence
        ]
    ):
        return jsonify({
            "error": "Each stat must be between 1 and 20."
        }), 400

    # --------------------------------------------------------
    # Create character
    # --------------------------------------------------------

    game.stats = {
        "name": name,
        "class": character_class,
        "backstory": backstory,

        "level": 1,

        "hp": 20,
        "max_hp": 20,

        "strength": strength,
        "dexterity": dexterity,
        "intelligence": intelligence,

        "gold": 25,
        "xp": 0
    }

    game.inventory["items"] = [
        {
            "name": "Simple Weapon",
            "type": "weapon",
            "damage": "1d6"
        },
        {
            "name": "Healing Potion",
            "type": "consumable",
            "effect": "Restore 10 HP",
            "quantity": 1
        }
    ]

    return jsonify({
        "success": True,
        "stats": game.stats,
        "inventory": game.inventory
    })


# ============================================================
# PREMADE CHARACTER
# ============================================================

@app.route("/api/create-class", methods=["POST"])
def create_class():

    data = request.json or {}

    name = data.get("name", "").strip()
    character_class = data.get("class", "").strip()

    if not name:
        return jsonify({
            "error": "Character name is required."
        }), 400

    presets = {

        "Warrior": {
            "hp": 28,
            "max_hp": 28,
            "strength": 16,
            "dexterity": 10,
            "intelligence": 8,
            "gold": 30,

            "items": [
                {
                    "name": "Iron Longsword",
                    "type": "weapon",
                    "damage": "1d8"
                },
                {
                    "name": "Wooden Shield",
                    "type": "armor",
                    "defense": 2
                },
                {
                    "name": "Healing Potion",
                    "type": "consumable",
                    "effect": "Restore 10 HP",
                    "quantity": 1
                }
            ]
        },

        "Rogue": {
            "hp": 20,
            "max_hp": 20,
            "strength": 10,
            "dexterity": 16,
            "intelligence": 12,
            "gold": 25,

            "items": [
                {
                    "name": "Iron Dagger",
                    "type": "weapon",
                    "damage": "1d6"
                },
                {
                    "name": "Lockpicks",
                    "type": "tool"
                },
                {
                    "name": "Healing Potion",
                    "type": "consumable",
                    "effect": "Restore 10 HP",
                    "quantity": 1
                }
            ]
        },

        "Mage": {
            "hp": 16,
            "max_hp": 16,
            "strength": 7,
            "dexterity": 12,
            "intelligence": 18,
            "gold": 20,

            "items": [
                {
                    "name": "Oak Staff",
                    "type": "weapon",
                    "damage": "1d6"
                },
                {
                    "name": "Spellbook",
                    "type": "magic",
                    "spells": [
                        "Fire Bolt",
                        "Arcane Shield"
                    ]
                },
                {
                    "name": "Mana Potion",
                    "type": "consumable",
                    "effect": "Restore magical energy",
                    "quantity": 1
                }
            ]
        }
    }

    if character_class not in presets:
        return jsonify({
            "error": "Unknown character class."
        }), 400

    preset = presets[character_class]

    game.stats = {
        "name": name,
        "class": character_class,
        "level": 1,

        "hp": preset["hp"],
        "max_hp": preset["max_hp"],

        "strength": preset["strength"],
        "dexterity": preset["dexterity"],
        "intelligence": preset["intelligence"],

        "gold": preset["gold"],
        "xp": 0
    }

    game.inventory["items"] = preset["items"]

    return jsonify({
        "success": True,
        "stats": game.stats,
        "inventory": game.inventory
    })


# ============================================================
# START LOCATION
# ============================================================

@app.route("/api/start", methods=["POST"])
def start_game():

    data = request.json or {}

    location = data.get("location")

    if location not in game.scenes:
        return jsonify({
            "error": "Invalid starting location."
        }), 400

    game.current_scene = location

    # Clear old conversation.
    game.chat_history.clear()

    opening = game.run_turn(
        """
Start the adventure now.

The player has just arrived at their selected starting location.

Introduce the character naturally without repeating their
entire stats.

Describe only the details that matter immediately.

Create an interesting event or problem that is happening NOW.

Introduce at most two NPCs.

Do not explain the entire mystery.

Do not give numbered choices.

Do not railroad the player.

Make the opening feel like a playable RPG scene rather than
a novel.

Leave the player with something interesting to react to.
"""
    )

    return jsonify({
        "success": True,
        "opening": opening,
        "state": {
            "stats": game.stats,
            "inventory": game.inventory,
            "current_scene": game.current_scene,
            "scene": game.scenes[game.current_scene]
        }
    })


# ============================================================
# PLAYER ACTION
# ============================================================

@app.route("/api/action", methods=["POST"])
def player_action():

    data = request.json or {}

    action = data.get("action", "").strip()

    if not action:
        return jsonify({
            "error": "Action cannot be empty."
        }), 400

    try:

        response = game.run_turn(action)

        current_scene = game.scenes.get(
            game.current_scene,
            {}
        )

        scene_npcs = []

        for npc_name in current_scene.get("npcs", []):

            if npc_name in game.npcs:

                scene_npcs.append(
                    game.npcs[npc_name]
                )

        return jsonify({

            "success": True,

            "response": response,

            "stats": game.stats,

            "inventory": game.inventory,

            "current_scene": game.current_scene,

            "scene": current_scene,

            "npcs": scene_npcs
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
