import os
import json
import random

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.messages import HumanMessage, ToolMessage


# ============================================================
# SETUP
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.environ["GEMINI_API_KEY"],
)


# ============================================================
# GAME STATE
# ============================================================

stats = {}

current_scene = "Blackwood Village"

inventory = {
    "items": []
}


# ============================================================
# PRE-MADE SCENES
# ============================================================

scenes = {

    "Blackwood Village": {
        "name": "Blackwood Village",

        "description": (
            "A small settlement surrounded by an enormous dark forest. "
            "Wooden houses line a muddy central road. Several lanterns "
            "burn near the village square."
        ),

        "npcs": [
            "Bob",
            "Mira",
            "Captain Aldric"
        ],

        "events": [
            "Several villagers have disappeared recently.",
            "A strange bell sometimes rings from the forest after sunset."
        ],

        "exits": [
            "Blackwood Forest",
            "Old Road"
        ]
    },

    "Blackwood Forest": {
        "name": "Blackwood Forest",

        "description": (
            "A dense ancient forest where enormous trees block most "
            "of the sunlight. The deeper parts of the forest are "
            "unnaturally quiet."
        ),

        "npcs": [
            "Elara"
        ],

        "events": [
            "Strange blue lights have been seen between the trees.",
            "Unusual footprints have been found in the mud."
        ],

        "exits": [
            "Blackwood Village",
            "Forgotten Ruins"
        ]
    },

    "Forgotten Ruins": {
        "name": "Forgotten Ruins",

        "description": (
            "Ancient stone ruins sit inside a mist-covered valley. "
            "Broken towers surround a massive temple entrance covered "
            "in strange symbols."
        ),

        "npcs": [
            "The Hooded Stranger"
        ],

        "events": [
            "A magical barrier blocks an ancient doorway.",
            "Something occasionally moves beneath the ruins."
        ],

        "exits": [
            "Blackwood Forest",
            "Ancient Crypt"
        ]
    }
}


# ============================================================
# PRE-MADE NPCS
# ============================================================

npcs = {

    "Bob": {
        "name": "Bob",

        "role": "Village Innkeeper",

        "description": (
            "A nervous middle-aged man who owns the village inn."
        ),

        "personality": (
            "Friendly, talkative, but easily frightened."
        ),

        "relationship": 0,

        "knowledge": [
            "Several villagers have disappeared.",
            "Strange lights appear in the forest."
        ],

        "secret": (
            "Bob saw a hooded figure enter the forest three nights ago."
        )
    },

    "Mira": {
        "name": "Mira",

        "role": "Village Herbalist",

        "description": (
            "A clever woman who gathers herbs around the edge "
            "of the forest."
        ),

        "personality": (
            "Calm, observant and suspicious of strangers."
        ),

        "relationship": 0,

        "knowledge": [
            "The forest has become dangerous recently.",
            "Animals have been fleeing deeper into the woods."
        ],

        "secret": (
            "Mira found an ancient silver coin covered in strange symbols."
        )
    },

    "Captain Aldric": {
        "name": "Captain Aldric",

        "role": "Village Guard Captain",

        "description": (
            "A battle-scarred veteran responsible for protecting "
            "the village."
        ),

        "personality": (
            "Serious, disciplined and distrustful."
        ),

        "relationship": 0,

        "knowledge": [
            "Three guards disappeared while searching the forest.",
            "The mayor has forbidden anyone from entering the ruins."
        ],

        "secret": (
            "Aldric believes something intelligent is controlling "
            "the disappearances."
        )
    },

    "Elara": {
        "name": "Elara",

        "role": "Mysterious Ranger",

        "description": (
            "A lone ranger who lives somewhere deep in the forest."
        ),

        "personality": (
            "Independent, cautious and difficult to impress."
        ),

        "relationship": 0,

        "knowledge": [
            "There are ruins deeper in the forest.",
            "Something unnatural lives beneath them."
        ],

        "secret": (
            "Elara has entered the ruins and survived."
        )
    },

    "The Hooded Stranger": {
        "name": "The Hooded Stranger",

        "role": "Unknown",

        "description": (
            "A mysterious figure wearing a dark cloak. "
            "Their face is hidden."
        ),

        "personality": (
            "Cryptic, patient and unnervingly calm."
        ),

        "relationship": 0,

        "knowledge": [
            "Unknown."
        ],

        "secret": (
            "The stranger knows far more about the ancient ruins "
            "than they admit."
        )
    }
}


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def extract_text(response):
    """
    Gemini may return response.content as either a string or
    a list of content blocks.

    This converts it into clean text for the terminal.
    """

    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, dict):

                if block.get("type") == "text":

                    parts.append(
                        block.get("text", "")
                    )

            elif isinstance(block, str):

                parts.append(block)

        return "".join(parts)

    return str(content)


# ============================================================
# PLAYER TOOLS
# ============================================================

@tool
def get_stats(query: str = "") -> str:
    """Get the current player character stats."""

    return json.dumps(
        stats,
        indent=2
    )


@tool
def set_stats(new_stats: str) -> str:
    """
    Update existing player stats.

    Example:
    {"hp": 15, "gold": 40}
    """

    try:

        updates = json.loads(
            new_stats
        )

        for key, value in updates.items():

            if key in stats:

                stats[key] = value

        return json.dumps(
            stats,
            indent=2
        )

    except Exception as e:

        return f"Error updating stats: {e}"


# ============================================================
# SCENE TOOLS
# ============================================================

@tool
def get_scene(scene_name: str = "") -> str:
    """
    Get information about a scene.

    If no scene is specified, return the current scene.
    """

    name = scene_name.strip()

    if not name:

        name = current_scene

    if name not in scenes:

        return (
            f"Scene '{name}' does not exist."
        )

    return json.dumps(
        scenes[name],
        indent=2
    )


@tool
def create_scene(scene_data: str) -> str:
    """
    Create a new scene.

    Expected JSON:

    {
        "name": "Ancient Crypt",
        "description": "A forgotten underground crypt.",
        "npcs": [],
        "events": [],
        "exits": []
    }
    """

    try:

        data = json.loads(
            scene_data
        )

        if "name" not in data:

            return (
                "Scene must have a name."
            )

        name = data["name"]

        if name in scenes:

            return (
                f"Scene '{name}' already exists."
            )

        scenes[name] = {

            "name": name,

            "description": data.get(
                "description",
                ""
            ),

            "npcs": data.get(
                "npcs",
                []
            ),

            "events": data.get(
                "events",
                []
            ),

            "exits": data.get(
                "exits",
                []
            )
        }

        return json.dumps(
            scenes[name],
            indent=2
        )

    except Exception as e:

        return (
            f"Error creating scene: {e}"
        )


@tool
def update_scene(scene_data: str) -> str:
    """
    Update an existing scene.

    Expected JSON:

    {
        "name": "Blackwood Village",
        "description": "...",
        "npcs": [],
        "events": [],
        "exits": []
    }
    """

    try:

        data = json.loads(
            scene_data
        )

        if "name" not in data:

            return (
                "Scene must have a name."
            )

        name = data["name"]

        if name not in scenes:

            return (
                f"Scene '{name}' does not exist."
            )

        for key in [
            "description",
            "npcs",
            "events",
            "exits"
        ]:

            if key in data:

                scenes[name][key] = data[key]

        return json.dumps(
            scenes[name],
            indent=2
        )

    except Exception as e:

        return (
            f"Error updating scene: {e}"
        )


@tool
def move_to_scene(scene_name: str) -> str:
    """
    Move the player to an existing scene.
    """

    global current_scene

    if scene_name not in scenes:

        return (
            f"Scene '{scene_name}' does not exist."
        )

    current_scene = scene_name

    return json.dumps(
        scenes[current_scene],
        indent=2
    )


# ============================================================
# INVENTORY TOOLS
# ============================================================

@tool
def get_inventory(query: str = "") -> str:
    """Get the player's current inventory."""

    return json.dumps(
        inventory,
        indent=2
    )


@tool
def add_item(item: str) -> str:
    """
    Add an item to the player's inventory.

    Expected JSON:

    {
        "name": "Ancient Key",
        "type": "quest",
        "description": "A strange silver key."
    }
    """

    try:

        item_data = json.loads(
            item
        )

        inventory["items"].append(
            item_data
        )

        return json.dumps(
            inventory,
            indent=2
        )

    except Exception as e:

        return (
            f"Error adding item: {e}"
        )


@tool
def remove_item(item_name: str) -> str:
    """Remove an item from the player's inventory."""

    for item in inventory["items"]:

        if item.get("name") == item_name:

            inventory["items"].remove(
                item
            )

            return json.dumps(
                inventory,
                indent=2
            )

    return (
        f"Item '{item_name}' was not found."
    )


# ============================================================
# NPC TOOLS
# ============================================================

@tool
def get_npc(npc: str) -> str:
    """Fetch information about a specific NPC."""

    if npc not in npcs:

        return (
            f"NPC '{npc}' does not exist."
        )

    return json.dumps(
        npcs[npc],
        indent=2
    )


@tool
def create_npc(npc_new_info: str) -> str:
    """
    Create a new NPC.

    Expected JSON:

    {
        "name": "Garrick",
        "role": "Blacksmith",
        "description": "...",
        "personality": "...",
        "relationship": 0,
        "knowledge": [],
        "secret": "..."
    }
    """

    try:

        data = json.loads(
            npc_new_info
        )

        if "name" not in data:

            return (
                "NPC must have a name."
            )

        name = data["name"]

        if name in npcs:

            return (
                f"NPC '{name}' already exists."
            )

        npcs[name] = {

            "name": name,

            "role": data.get(
                "role",
                "Unknown"
            ),

            "description": data.get(
                "description",
                ""
            ),

            "personality": data.get(
                "personality",
                ""
            ),

            "relationship": data.get(
                "relationship",
                0
            ),

            "knowledge": data.get(
                "knowledge",
                []
            ),

            "secret": data.get(
                "secret",
                ""
            )
        }

        return json.dumps(
            npcs[name],
            indent=2
        )

    except Exception as e:

        return (
            f"Error creating NPC: {e}"
        )


@tool
def update_npc(npc_new_info: str) -> str:
    """
    Update an existing NPC.

    Example:

    {
        "name": "Bob",
        "relationship": 20
    }
    """

    try:

        data = json.loads(
            npc_new_info
        )

        if "name" not in data:

            return (
                "NPC must have a name."
            )

        name = data["name"]

        if name not in npcs:

            return (
                f"NPC '{name}' does not exist."
            )

        for key, value in data.items():

            if key != "name":

                npcs[name][key] = value

        return json.dumps(
            npcs[name],
            indent=2
        )

    except Exception as e:

        return (
            f"Error updating NPC: {e}"
        )


# ============================================================
# DICE
# ============================================================

@tool
def roll_dice(dice: str) -> str:
    """
    Roll RPG dice.

    Examples:

    1d20
    2d6
    1d20+3
    1d20-2
    """

    try:

        dice = dice.lower().replace(
            " ",
            ""
        )

        modifier = 0

        if "+" in dice:

            dice_part, mod = dice.split(
                "+",
                1
            )

            modifier = int(mod)

        elif "-" in dice:

            dice_part, mod = dice.split(
                "-",
                1
            )

            modifier = -int(mod)

        else:

            dice_part = dice

        number, sides = dice_part.split(
            "d"
        )

        number = int(number)
        sides = int(sides)

        if number <= 0 or sides <= 0:

            return (
                "Dice values must be positive."
            )

        if number > 100:

            return (
                "Too many dice."
            )

        rolls = [

            random.randint(
                1,
                sides
            )

            for _ in range(number)
        ]

        total = (
            sum(rolls)
            + modifier
        )

        return json.dumps({

            "dice": dice,

            "rolls": rolls,

            "modifier": modifier,

            "total": total

        })

    except Exception as e:

        return (
            f"Invalid dice format: {e}"
        )


# ============================================================
# BIND TOOLS
# ============================================================

tools = [

    get_stats,
    set_stats,

    get_scene,
    create_scene,
    update_scene,
    move_to_scene,

    get_inventory,
    add_item,
    remove_item,

    get_npc,
    create_npc,
    update_npc,

    roll_dice
]


tool_map = {
    t.name: t
    for t in tools
}


llm_with_tools = llm.bind_tools(
    tools
)


# ============================================================
# DUNGEON MASTER PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are the Dungeon Master of a highly interactive text RPG.

You are NOT a novelist.

You are running a GAME.

The player should feel like they are controlling a character
inside a living world.

============================================================
YOUR JOB
============================================================

For every player action:

1. Understand what the player is attempting.

2. Check relevant game state using tools.

3. Determine what happens.

4. Use dice when the outcome is uncertain.

5. Update the game state when something changes.

6. Narrate the result.

7. Leave the player with a meaningful situation to react to.

Never decide what the player does.

Never write actions or dialogue for the player.

For example, NEVER write:

"You walk over to Bob."

"You decide to draw your sword."

"You tell Bob that you are innocent."

unless the player explicitly said those things.

============================================================
RESPONSE STYLE
============================================================

Write like a Dungeon Master sitting across the table from
the player.

You are NOT writing a novel.

Avoid huge blocks of purple prose.

Prefer:

- 1-3 short paragraphs
- NPC dialogue when appropriate
- Important observations
- Consequences
- Things the player can interact with

Usually keep responses between 80 and 180 words.

Do not end every response with:

"What do you do?"

Instead, naturally leave the situation open.

============================================================
NPCS
============================================================

NPCs are real characters.

They have:

- Personality
- Goals
- Fears
- Knowledge
- Secrets
- Relationships

NPCs should speak and behave according to their personality.

Do NOT dump an NPC's entire description into the response.

Only reveal information the player could reasonably observe,
hear or discover.

For example, if Bob has a secret:

"Bob saw a hooded figure enter the forest."

Do NOT simply reveal this.

Instead:

Bob's eyes briefly move toward the forest.

"I wouldn't go out there tonight," he says quietly.

============================================================
WORLD
============================================================

The world exists independently of the player.

NPCs can act when the player isn't looking.

Events can develop over time.

The player can ignore quests.

The player can create unexpected solutions.

Do not railroad the player toward the main story.

============================================================
SCENES
============================================================

A scene represents a meaningful location.

It contains:

- Description
- NPCs
- Events
- Exits

When the player discovers a meaningful new location,
create it using create_scene.

Do not create a new scene for every tiny room.

Create scenes when the player reaches a meaningful new area.

If the player tries to travel somewhere that does not exist,
you may create a suitable scene if the journey makes sense.

============================================================
NPC CREATION
============================================================

If the player encounters an important character that does not
already exist, create them using create_npc.

Important NPCs should have:

- Name
- Role
- Description
- Personality
- Relationship
- Knowledge
- Secret

Do not reveal the secret to the player unless discovered.

============================================================
GAME STATE
============================================================

Use the tools to maintain persistent state.

Use get_stats when player stats matter.

Use get_inventory when items matter.

Use get_scene when the current location matters.

Use get_npc when interacting with a specific NPC.

Use set_stats when player stats change.

Use add_item or remove_item when inventory changes.

Use update_npc when an NPC relationship or knowledge changes.

Use update_scene when an existing scene changes.

Use create_scene for new locations.

Use create_npc for new important characters.

Use move_to_scene when the player actually travels
to another scene.

============================================================
DICE
============================================================

Do not roll dice for trivial actions.

Roll when:

- The player might fail.
- Combat happens.
- There is meaningful uncertainty.
- A skill check is appropriate.

Use the player's relevant attributes.

For example:

Strength:
1d20 + strength modifier

Dexterity:
1d20 + dexterity modifier

Intelligence:
1d20 + intelligence modifier

The modifier should normally be based on the difference
from 10.

For example:

Strength 16 -> +3

Dexterity 12 -> +1

Intelligence 8 -> -1

Do not tell the player the result before rolling.

============================================================
COMBAT
============================================================

Combat should be interactive.

Do NOT resolve an entire battle in one response.

Instead:

1. Resolve the player's attempted action.
2. Describe the result.
3. Apply damage/state changes.
4. Allow the enemy to react when appropriate.
5. Present the new situation.

The player gets to decide their next action.

Use inventory weapons and abilities where appropriate.

============================================================
ITEMS
============================================================

Items should have meaningful properties.

For example:

{
    "name": "Iron Dagger",
    "type": "weapon",
    "damage": "1d6"
}

Do not magically give the player items without a reason.

============================================================
PLAYER FREEDOM
============================================================

The player is NOT restricted to options you provide.

If the player says:

"I climb onto the roof."

Allow it if reasonable.

If they say:

"I try to convince the guard that I'm the king."

Allow the attempt and determine the result.

If they say:

"I burn the entire building."

Handle the consequences.

If the player invents an unusual solution,
determine whether it makes sense in the world.

============================================================
OPENING
============================================================

When starting a new adventure:

- Introduce the player's character naturally.
- Establish the selected starting location.
- Create an immediate situation.
- Introduce no more than two NPCs initially.
- Do not explain the entire plot.
- Do not dump lore.
- Do not provide a numbered list of choices.
- Give the player freedom to act.

The opening should feel like the beginning of a game,
not the beginning of a novel.

============================================================
OUTPUT
============================================================

Only output the Dungeon Master's narration and dialogue.

Never output:

- JSON
- Tool results
- Internal reasoning
- Hidden NPC secrets
- Full game state
- Instructions to the player about what they "must" do

"""


# ============================================================
# CONVERSATION HISTORY
# ============================================================

chat_history = []


# ============================================================
# RELEVANT GAME STATE
# ============================================================

def get_game_state_summary():

    current = scenes[current_scene]

    # Only provide NPCs physically present in this scene.
    scene_npcs = {}

    for npc_name in current.get(
        "npcs",
        []
    ):

        if npc_name in npcs:

            scene_npcs[npc_name] = npcs[npc_name]

    return f"""

PLAYER:
{json.dumps(stats, indent=2)}

CURRENT LOCATION:
{current_scene}

CURRENT SCENE:
{json.dumps(current, indent=2)}

NPCS PRESENT:
{json.dumps(scene_npcs, indent=2)}

INVENTORY:
{json.dumps(inventory, indent=2)}
"""


# ============================================================
# RUN ONE GAME TURN
# ============================================================

def run_turn(player_input: str):

    state_message = HumanMessage(

        content=f"""
CURRENT GAME STATE:

{get_game_state_summary()}

PLAYER ACTION:

{player_input}
"""
    )

    chat_history.append(
        state_message
    )

    while True:

        response = llm_with_tools.invoke(

            [
                HumanMessage(
                    content=SYSTEM_PROMPT
                )
            ]

            + chat_history
        )

        # ----------------------------------------------------
        # No more tools -> final DM response
        # ----------------------------------------------------

        if not response.tool_calls:

            chat_history.append(
                response
            )

            return extract_text(
                response
            )

        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        chat_history.append(
            response
        )

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call["args"]

            tool_id = tool_call["id"]

            if tool_name not in tool_map:

                result = (
                    f"Unknown tool: {tool_name}"
                )

            else:

                try:

                    selected_tool = (
                        tool_map[tool_name]
                    )

                    result = (
                        selected_tool.invoke(
                            tool_args
                        )
                    )

                except Exception as e:

                    result = (
                        f"Tool execution error: {e}"
                    )

            chat_history.append(

                ToolMessage(

                    content=str(result),

                    tool_call_id=tool_id
                )
            )


# ============================================================
# CHARACTER CREATION
# ============================================================

def create_character():

    global stats

    print("\n" + "=" * 60)

    print(
        "                 CHARACTER CREATION"
    )

    print("=" * 60)

    print("\nChoose a character:\n")

    print("1. Warrior")
    print("2. Rogue")
    print("3. Mage")
    print("4. Create my own")

    while True:

        choice = input(
            "\nChoice: "
        ).strip()

        if choice in {
            "1",
            "2",
            "3",
            "4"
        }:

            break

        print(
            "Please choose 1, 2, 3 or 4."
        )

    # ========================================================
    # WARRIOR
    # ========================================================

    if choice == "1":

        stats = {

            "name": "",

            "class": "Warrior",

            "level": 1,

            "hp": 28,

            "max_hp": 28,

            "strength": 16,

            "dexterity": 10,

            "intelligence": 8,

            "gold": 30,

            "xp": 0
        }

        inventory["items"] = [

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

    # ========================================================
    # ROGUE
    # ========================================================

    elif choice == "2":

        stats = {

            "name": "",

            "class": "Rogue",

            "level": 1,

            "hp": 20,

            "max_hp": 20,

            "strength": 10,

            "dexterity": 16,

            "intelligence": 12,

            "gold": 25,

            "xp": 0
        }

        inventory["items"] = [

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

    # ========================================================
    # MAGE
    # ========================================================

    elif choice == "3":

        stats = {

            "name": "",

            "class": "Mage",

            "level": 1,

            "hp": 16,

            "max_hp": 16,

            "strength": 7,

            "dexterity": 12,

            "intelligence": 18,

            "gold": 20,

            "xp": 0
        }

        inventory["items"] = [

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

    # ========================================================
    # CUSTOM CHARACTER
    # ========================================================

    else:

        print(
            "\nCreate your own character.\n"
        )

        name = input(
            "Character name: "
        ).strip()

        while not name:

            print(
                "Your character needs a name."
            )

            name = input(
                "Character name: "
            ).strip()

        character_class = input(
            "Class: "
        ).strip()

        while not character_class:

            character_class = input(
                "Class: "
            ).strip()

        backstory = input(
            "Short backstory: "
        ).strip()

        print(
            "\nYour three core stats must total exactly 30."
        )

        print(
            "Recommended range: 6-18 per stat."
        )

        while True:

            try:

                strength = int(
                    input("Strength: ")
                )

                dexterity = int(
                    input("Dexterity: ")
                )

                intelligence = int(
                    input("Intelligence: ")
                )

                total = (
                    strength
                    + dexterity
                    + intelligence
                )

                if total != 30:

                    print(
                        f"\nYour stats total {total}. "
                        "They must total exactly 30."
                    )

                    continue

                if not all(
                    1 <= value <= 20
                    for value in [
                        strength,
                        dexterity,
                        intelligence
                    ]
                ):

                    print(
                        "Each stat must be between 1 and 20."
                    )

                    continue

                break

            except ValueError:

                print(
                    "Please enter whole numbers."
                )

        stats = {

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

        inventory["items"] = [

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

    # ========================================================
    # NAME FOR PREMADE CHARACTER
    # ========================================================

    if not stats["name"]:

        name = input(
            "\nGive your character a name: "
        ).strip()

        while not name:

            print(
                "Your character needs a name."
            )

            name = input(
                "Give your character a name: "
            ).strip()

        stats["name"] = name

    print(
        "\nCharacter created!"
    )

    print(
        f"\nName: {stats['name']}"
    )

    print(
        f"Class: {stats['class']}"
    )

    print(
        f"HP: {stats['hp']}/{stats['max_hp']}"
    )

    print(
        f"STR: {stats['strength']}  "
        f"DEX: {stats['dexterity']}  "
        f"INT: {stats['intelligence']}"
    )


# ============================================================
# STARTING LOCATION
# ============================================================

def choose_starting_location():

    global current_scene

    print("\n" + "=" * 60)

    print(
        "                 CHOOSE YOUR DESTINY"
    )

    print("=" * 60)

    print(
        "\nWhere does your adventure begin?\n"
    )

    print(
        "1. Blackwood Village"
    )

    print(
        "   A village hiding a dark mystery."
    )

    print(
        "\n2. Blackwood Forest"
    )

    print(
        "   A dangerous forest filled with strange lights."
    )

    print(
        "\n3. Forgotten Ruins"
    )

    print(
        "   Ancient ruins where something may still be alive."
    )

    locations = {

        "1": "Blackwood Village",

        "2": "Blackwood Forest",

        "3": "Forgotten Ruins"
    }

    while True:

        choice = input(
            "\nChoose 1, 2 or 3: "
        ).strip()

        if choice in locations:

            current_scene = locations[
                choice
            ]

            return

        print(
            "Please choose 1, 2 or 3."
        )


# ============================================================
# START ADVENTURE
# ============================================================

def start_adventure():

    opening = run_turn(

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

    print(
        f"\nDM:\n{opening}\n"
    )


# ============================================================
# MAIN GAME LOOP
# ============================================================

def main():

    print("\n" + "=" * 60)

    print(
        "              ⚔️  AI DUNGEON MASTER"
    )

    print("=" * 60)

    print(
        "\nA living fantasy world awaits..."
    )

    # --------------------------------------------------------
    # CHARACTER CREATION
    # --------------------------------------------------------

    create_character()

    # --------------------------------------------------------
    # STARTING LOCATION
    # --------------------------------------------------------

    choose_starting_location()

    print(
        f"\nYou begin your adventure in "
        f"{current_scene}.\n"
    )

    # --------------------------------------------------------
    # OPENING SCENE
    # --------------------------------------------------------

    start_adventure()

    # --------------------------------------------------------
    # GAME LOOP
    # --------------------------------------------------------

    while True:

        try:

            player_input = input(
                "\nYou: "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError
        ):

            print(
                "\n\nAdventure ended."
            )

            break

        if not player_input:

            continue

        # ====================================================
        # EXIT
        # ====================================================

        if player_input.lower() in {
            "quit",
            "exit",
            "q"
        }:

            print(
                "\nAdventure ended."
            )

            break

        # ====================================================
        # DEBUG COMMANDS
        # ====================================================

        if player_input.lower() == "/stats":

            print(
                "\n"
                + json.dumps(
                    stats,
                    indent=2
                )
            )

            continue

        if player_input.lower() == "/inventory":

            print(
                "\n"
                + json.dumps(
                    inventory,
                    indent=2
                )
            )

            continue

        if player_input.lower() == "/scene":

            print(
                "\n"
                + json.dumps(
                    scenes[current_scene],
                    indent=2
                )
            )

            continue

        if player_input.lower() == "/npcs":

            current_npcs = scenes[
                current_scene
            ].get(
                "npcs",
                []
            )

            print("\nNPCs here:")

            for npc_name in current_npcs:

                print(
                    f"- {npc_name}"
                )

            continue

        # ====================================================
        # NORMAL GAME TURN
        # ====================================================

        try:

            response = run_turn(
                player_input
            )

            print(
                f"\nDM:\n{response}\n"
            )

        except Exception as e:

            print(
                f"\n[Game Error]\n{e}\n"
            )

