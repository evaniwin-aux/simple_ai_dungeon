let selectedClass = null;


/* ============================================================
   CHARACTER CLASS
   ============================================================ */

function selectClass(characterClass) {

    selectedClass = characterClass;

    const info = document.getElementById("class-info");

    const descriptions = {
        Warrior: "Strong melee fighter with high HP.",
        Rogue: "Fast and agile fighter specializing in Dexterity.",
        Mage: "Fragile spellcaster with powerful Intelligence."
    };

    info.innerHTML = `
        <p>
            <strong>${escapeHTML(characterClass)}</strong>
            — ${escapeHTML(descriptions[characterClass])}
        </p>
    `;
}


/* ============================================================
   CREATE CHARACTER
   ============================================================ */

async function createCharacter() {

    const name = document
        .getElementById("character-name")
        .value
        .trim();

    const backstory = document
        .getElementById("backstory")
        .value
        .trim();

    if (!name) {
        showCreationError("Enter a character name.");
        return;
    }


    /* --------------------------------------------------------
       PRE-MADE CLASS
       -------------------------------------------------------- */

    if (selectedClass) {

        try {

            const response = await fetch(
                "/api/create-class",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        class: selectedClass
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                showCreationError(
                    data.error || "Failed to create character."
                );

                return;
            }

            showLocationScreen();

        } catch (error) {

            showCreationError(
                "Could not connect to the server."
            );

            console.error(error);
        }

        return;
    }


    /* --------------------------------------------------------
       CUSTOM CHARACTER
       -------------------------------------------------------- */

    const strength = Number(
        document
            .getElementById("strength")
            .value
    );

    const dexterity = Number(
        document
            .getElementById("dexterity")
            .value
    );

    const intelligence = Number(
        document
            .getElementById("intelligence")
            .value
    );


    if (
        strength
        + dexterity
        + intelligence
        !== 30
    ) {

        showCreationError(
            "Strength, Dexterity and Intelligence must total exactly 30."
        );

        return;
    }


    if (
        ![strength, dexterity, intelligence]
            .every(value => value >= 1 && value <= 20)
    ) {

        showCreationError(
            "Each stat must be between 1 and 20."
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/create-character",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    name: name,

                    class: "Adventurer",

                    backstory: backstory,

                    strength: strength,

                    dexterity: dexterity,

                    intelligence: intelligence
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            showCreationError(
                data.error || "Failed to create character."
            );

            return;
        }


        showLocationScreen();

    } catch (error) {

        showCreationError(
            "Could not connect to the server."
        );

        console.error(error);
    }
}


/* ============================================================
   SHOW LOCATION SCREEN
   ============================================================ */

function showLocationScreen() {

    document
        .getElementById("character-screen")
        .classList.add("hidden");

    document
        .getElementById("location-screen")
        .classList.remove("hidden");
}


/* ============================================================
   ERROR MESSAGE
   ============================================================ */

function showCreationError(message) {

    const element =
        document.getElementById("creation-error");

    element.textContent = message;
}


/* ============================================================
   START GAME
   ============================================================ */

async function startGame(location) {

    try {

        const response = await fetch(
            "/api/start",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    location: location
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(
                data.error || "Could not start game."
            );

            return;
        }


        document
            .getElementById("location-screen")
            .classList.add("hidden");

        document
            .getElementById("game-screen")
            .classList.remove("hidden");


        clearChat();


        addMessage(
            "dm",
            data.opening
        );


        updateState(data);


        document
            .getElementById("action-input")
            .focus();


    } catch (error) {

        console.error(error);

        alert(
            "Could not connect to the server."
        );
    }
}


/* ============================================================
   ACTION FORM
   ============================================================ */

document
    .getElementById("action-form")
    .addEventListener(
        "submit",
        handleAction
    );


async function handleAction(event) {

    event.preventDefault();


    const input =
        document.getElementById(
            "action-input"
        );


    const action =
        input.value.trim();


    if (!action) {
        return;
    }


    /* Show player action */

    addMessage(
        "player",
        action
    );


    input.value = "";

    input.disabled = true;


    try {

        const response = await fetch(
            "/api/action",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    action: action
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            addMessage(
                "dm",
                "Game error: "
                + (
                    data.error
                    || "Unknown error."
                )
            );

            return;
        }


        addMessage(
            "dm",
            data.response
        );


        updateState(data);


    } catch (error) {

        console.error(error);


        addMessage(
            "dm",
            "Connection error: "
            + error.message
        );


    } finally {

        input.disabled = false;

        input.focus();
    }
}


/* ============================================================
   CHAT
   ============================================================ */

function clearChat() {

    document
        .getElementById("chat")
        .innerHTML = "";
}


function addMessage(type, text) {

    const chat =
        document.getElementById("chat");


    const message =
        document.createElement("div");


    message.className =
        "message " + type;


    const label =
        type === "dm"
            ? "Dungeon Master"
            : "You";


    message.innerHTML = `

        <div class="message-label">
            ${escapeHTML(label)}
        </div>

        <div>
            ${formatText(text)}
        </div>

    `;


    chat.appendChild(message);


    chat.scrollTop =
        chat.scrollHeight;
}


/* ============================================================
   SAFE TEXT FORMATTING
   ============================================================ */

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatText(text) {

    return escapeHTML(text)
        .replace(/\n/g, "<br>");
}


/* ============================================================
   UPDATE GAME STATE
   ============================================================ */

function updateState(data) {

    if (data.stats) {

        updateStats(
            data.stats
        );
    }


    if (data.inventory) {

        updateInventory(
            data.inventory
        );
    }


    if (data.scene) {

        updateScene(
            data.scene,
            data.current_scene
        );
    }


    if (data.npcs) {

        updateNPCs(
            data.npcs
        );
    }
}


/* ============================================================
   PLAYER STATS
   ============================================================ */

function updateStats(stats) {

    const name =
        stats.name || "Adventurer";


    const characterClass =
        stats.class || "Adventurer";


    const level =
        stats.level || 1;


    document
        .getElementById("player-name")
        .textContent = name;


    document
        .getElementById("player-class")
        .textContent =
            `${characterClass} • Level ${level}`;


    /* --------------------------------------------------------
       HP
       -------------------------------------------------------- */

    const maxHP =
        Number(stats.max_hp) || 1;


    const hp =
        Math.max(
            0,
            Math.min(
                Number(stats.hp) || 0,
                maxHP
            )
        );


    const hpPercent =
        (hp / maxHP) * 100;


    document
        .getElementById("hp-bar")
        .style.width =
            `${hpPercent}%`;


    document
        .getElementById("hp-text")
        .textContent =
            `${hp} / ${maxHP}`;


    /* --------------------------------------------------------
       XP
       -------------------------------------------------------- */

    const xp =
        Number(stats.xp) || 0;


    const xpForLevel =
        100;


    const xpPercent =
        Math.min(
            100,
            (xp % xpForLevel)
            / xpForLevel
            * 100
        );


    document
        .getElementById("xp-bar")
        .style.width =
            `${xpPercent}%`;


    document
        .getElementById("xp-text")
        .textContent =
            `${xp} XP`;


    /* --------------------------------------------------------
       ATTRIBUTES
       -------------------------------------------------------- */

    updateAttribute(
        "str",
        Number(stats.strength) || 0
    );


    updateAttribute(
        "dex",
        Number(stats.dexterity) || 0
    );


    updateAttribute(
        "int",
        Number(stats.intelligence) || 0
    );


    /* --------------------------------------------------------
       GOLD
       -------------------------------------------------------- */

    document
        .getElementById("gold")
        .textContent =
            Number(stats.gold) || 0;
}


function updateAttribute(prefix, value) {

    const percent =
        Math.min(
            100,
            Math.max(
                0,
                value / 20 * 100
            )
        );


    document
        .getElementById(
            `${prefix}-bar`
        )
        .style.width =
            `${percent}%`;


    document
        .getElementById(
            `${prefix}-value`
        )
        .textContent =
            value;
}


/* ============================================================
   INVENTORY
   ============================================================ */

function updateInventory(inventory) {

    const container =
        document.getElementById(
            "inventory-list"
        );


    container.innerHTML = "";


    const items =
        inventory.items || [];


    if (items.length === 0) {

        container.innerHTML = `

            <div class="inventory-item">

                <small>
                    Inventory is empty.
                </small>

            </div>

        `;

        return;
    }


    items.forEach(item => {

        const div =
            document.createElement("div");


        div.className =
            "inventory-item";


        let details = "";


        if (item.type) {

            details +=
                `${item.type}`;
        }


        if (item.damage) {

            details +=
                ` • Damage: ${item.damage}`;
        }


        if (item.defense) {

            details +=
                ` • Defense: ${item.defense}`;
        }


        if (item.effect) {

            details +=
                ` • ${item.effect}`;
        }


        if (item.quantity) {

            details +=
                ` • Qty: ${item.quantity}`;
        }


        div.innerHTML = `

            <strong>
                ${escapeHTML(
                    item.name || "Unknown Item"
                )}
            </strong>

            <small>
                ${escapeHTML(details)}
            </small>

        `;


        container.appendChild(div);
    });
}


/* ============================================================
   SCENE
   ============================================================ */

function updateScene(scene, currentScene) {

    document
        .getElementById("scene-name")
        .textContent =
            currentScene
            || scene.name
            || "Unknown Location";


    document
        .getElementById("scene-description")
        .textContent =
            scene.description
            || "";
}


/* ============================================================
   NPCS
   ============================================================ */

function updateNPCs(npcs) {

    const container =
        document.getElementById(
            "npc-list"
        );


    container.innerHTML = "";


    if (!npcs || npcs.length === 0) {

        container.innerHTML = `
            <small>No one nearby.</small>
        `;

        return;
    }


    npcs.forEach(npc => {

        const div =
            document.createElement("div");


        div.className =
            "npc";


        div.innerHTML = `

            <strong>
                ${escapeHTML(
                    npc.name || "Unknown"
                )}
            </strong>

            <small>
                ${escapeHTML(
                    npc.role || ""
                )}
            </small>

        `;


        container.appendChild(div);
    });
}
