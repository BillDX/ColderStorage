from __future__ import annotations


class Game:
    """State and command parser for Cold Storage."""

    ROOM_NAMES = {
        "reception": "Reception",
        "hallway": "The Pale Corridor",
        "break_room": "The Last Coffee",
        "mechanical_room": "The Humming Closet",
        "server_room": "Rack Room",
        "noc": "The Observatory of Bad Decisions",
        "cold_aisle": "The Frozen Stack",
    }

    DIRECTIONS = {
        "n": "north",
        "s": "south",
        "e": "east",
        "w": "west",
        "north": "north",
        "south": "south",
        "east": "east",
        "west": "west",
    }

    def __init__(self) -> None:
        self.location = "reception"
        self.inventory: list[str] = []
        self.won = False
        self.flags: set[str] = set()
        self.completed_goals: set[str] = set()
        self.room_items: dict[str, list[str]] = {
            "reception": ["lanyard", "hoodie"],
            "hallway": [],
            "break_room": ["coffee pod", "mug"],
            "mechanical_room": [],
            "server_room": [],
            "noc": [],
            "cold_aisle": ["exit key"],
        }

    def items_at(self, room: str) -> list[str]:
        return list(self.room_items.get(room, []))

    def execute(self, command: str) -> str:
        cleaned = " ".join(command.strip().lower().split())
        if not cleaned:
            return "You say nothing. The silence is not golden; it is 19-inch rack gray."
        verb, _, rest = cleaned.partition(" ")
        rest = rest.strip()

        if verb in self.DIRECTIONS:
            return self._go(self.DIRECTIONS[verb])
        if verb in {"look", "l"}:
            return self._look()
        if verb == "open":
            return self._open(rest)
        if verb in {"examine", "x"}:
            return self._examine(rest)
        if verb in {"take", "get", "grab"}:
            return self._take(rest)
        if verb in {"inventory", "inv", "i"}:
            return self._show_inventory()
        if verb == "drop":
            return self._drop(rest)
        if verb in {"goals", "goal", "objectives"}:
            return self._show_goals()
        if verb in {"hint", "helpme"}:
            return self._hint()
        if verb in {"search", "look under"}:
            return self._search(rest)
        if verb == "use":
            return self._use(rest)
        if verb == "talk":
            target = rest.removeprefix("to ").strip()
            return self._talk(target)
        if verb == "give":
            return self._give(rest)
        if verb == "type":
            return self._type_password(rest)
        if verb in {"wear", "don"}:
            return self._wear(rest)
        if verb == "pull":
            return self._pull(rest)
        if verb == "sudo":
            return (
                "You are not in the sudoers file. This incident has been reported "
                "to a ghost, a compliance officer, and your mother."
            )

        return (
            "The datacenter hums. Your command does not compute. "
            "Try LOOK, INVENTORY, GOALS, or HINT."
        )

    def _go(self, direction: str) -> str:
        exits = {
            ("reception", "north"): "hallway",
            ("hallway", "south"): "reception",
            ("hallway", "east"): "break_room",
            ("break_room", "west"): "hallway",
            ("break_room", "north"): "mechanical_room",
            ("mechanical_room", "south"): "break_room",
            ("hallway", "west"): "server_room",
            ("server_room", "east"): "hallway",
            ("hallway", "north"): "noc",
            ("noc", "south"): "hallway",
            ("server_room", "north"): "cold_aisle",
            ("cold_aisle", "south"): "server_room",
        }
        key = (self.location, direction)
        if key == ("reception", "north") and "lanyard" not in self.inventory:
            return (
                "The security door gives you a red glare. A sign says EMPLOYEES ONLY. "
                "Your lanyard is probably in the reception desk."
            )
        if key == ("server_room", "north") and "hoodie_worn" not in self.flags:
            return (
                "The cold aisle is forty degrees below comfortable and four degrees below legal. "
                "You need something warmer. The reception coat rack had a suspiciously available hoodie."
            )
        if key == ("reception", "south"):
            return self._try_to_escape()
        destination = exits.get(key)
        if destination is None:
            return "There is no obvious way to go that direction."
        self.location = destination
        return self._room_arrival(destination)

    def _room_arrival(self, room: str) -> str:
        return self._room_description(room)

    def _room_description(self, room: str) -> str:
        descriptions = {
            "reception": (
                "RECEPTION. The EMERGENCY EXIT is sealed and quietly judging you. "
                "A reception desk has a single stubborn DRAWER. A coat rack offers a "
                "corporate HOODIE with the slogan COLD STORAGE: WHY WAIT FOR THE CLOUD? "
                "The dead ficus watches with plastic indifference. The employee door leads north."
            ),
            "hallway": (
                "THE PALE CORRIDOR. A VENDING MACHINE glows with stale snacks and one "
                "suspiciously practical purchase. MORTIMER CACHE, a translucent sysadmin ghost, "
                "hovers beside it, radiating unresolved tickets.\n"
                "Exits: east to the break room, west to the server room, north to the NOC, "
                "south to reception."
            ),
            "break_room": (
                "THE LAST COFFEE. A FRIDGE hums a note of institutional despair. The COFFEE "
                "MACHINE has a jar of COFFEE PODS beside it and a rack holding one MUG. "
                "Three motivational posters promise SYNERGY, FOCUS, and a THIRD THING. "
                "A STAFF ONLY door leads north."
            ),
            "mechanical_room": (
                "THE HUMMING CLOSET. A handle-less COOLANT VALVE waits in the pipework. "
                "A TOOLBOX sits nearby. The sign says FLOW 0%. PLEASE DO NOT LICK THE PIPES. "
                "The only exit is south."
            ),
            "server_room": (
                "RACK ROOM. Status LEDs blink in panic. The ALARM PANEL strobes above a rack "
                "labeled 'PRODUCTION (PROBABLY),' and a BLUE CABLE hangs beneath it with a "
                "warning tag. A frosty doorway leads north to the COLD AISLE. The hallway is east."
            ),
            "noc": (
                "THE OBSERVATORY OF BAD DECISIONS. Twelve monitors display twelve different "
                "graphs of the same disaster. A TERMINAL waits for root access. The hallway is south."
            ),
            "cold_aisle": (
                "THE FROZEN STACK. Your breath turns to fog. A red EMERGENCY EXIT KEY hangs "
                "from a frost-covered hook beside racks maintained at penguin-litigation "
                "temperatures. The server room is south."
            ),
        }
        return descriptions[room]

    def _look(self) -> str:
        return self._room_description(self.location)

    def _open(self, target: str) -> str:
        if target == "drawer":
            return self._open_drawer()
        if target in {"toolbox", "tool box"}:
            return self._open_toolbox()
        return f"The {target or 'thing'} does not open. It may be load-bearing."

    def _open_drawer(self) -> str:
        if self.location != "reception":
            return "You can't find a desk drawer here, which is honestly for the best."
        self.flags.add("drawer_open")
        return (
            "The drawer opens with a squelch. Inside, beside six expired ketchup packets, "
            "is an EMPLOYEE LANYARD. The photo is you from three years and two haircuts ago."
        )

    def _open_toolbox(self) -> str:
        if self.location != "mechanical_room":
            return "There is no toolbox here. The building has enough mysteries already."
        self.flags.add("toolbox_open")
        if "insulated gloves" not in self.room_items["mechanical_room"]:
            self.room_items["mechanical_room"].append("insulated gloves")
        return (
            "The toolbox opens with a metallic sigh. Inside: one INSULATED GLOVES, "
            "forty-seven identical screwdrivers, and a note reading 'IF FOUND, PANIC QUIETLY.'"
        )

    def _examine(self, target: str) -> str:
        if target in {"vending machine", "vending"}:
            if self.location != "hallway":
                return "There is no vending machine here."
            return (
                "The vending machine lists: A1 SALTED REGRETS, B2 ANCIENT GRANOLA, "
                "and B4 EMERGENCY VALVE WHEEL - 25 CENTS. The B4 coil looks load-bearing "
                "in a way no snack should."
            )
        if target in {"alarm panel", "alarm", "panel"} and self.location == "server_room":
            return (
                "The alarm panel flashes red. A laminated card reads: "
                "'IN EVENT OF STUCK ALARM, PULL THE BLUE CABLE. "
                "DO NOT PULL THE RED CABLE. RED IS FOR THE SPRINKLERS AND ALSO EMOTIONS.' "
                "The blue cable practically hums with bad decisions."
            )
        if target == "blue cable" and self.location == "server_room":
            return (
                "A blue cable labeled ALARM SENSE runs beneath the panel. "
                "The plastic warning tag says: INSULATED GLOVES REQUIRED. NO EXCEPTIONS, KEVIN."
            )
        if target in {"toolbox", "tool box"} and self.location == "mechanical_room":
            if "toolbox_open" in self.flags:
                return "The toolbox is open. Its screwdrivers are arranged by emotional damage."
            return "A battered toolbox is bolted to the wall. It might open."
        if target in {"coolant valve", "valve"} and self.location == "mechanical_room":
            return "A brass fitting with no wheel. It is waiting for the vending machine to solve its problems."
        if target in {"exit key", "emergency key"} and self.location == "cold_aisle":
            return (
                "A large red key hangs from a frost-covered hook. Its tag reads: "
                "EMERGENCY EXIT - USE ONLY DURING EMERGENCIES OR ESPECIALLY BAD TUESDAYS."
            )
        return f"You examine the {target or 'room'} closely. It has the texture of institutional urgency."

    def _search(self, thing: str) -> str:
        if thing in {"fridge", "refrigerator"} and self.location == "break_room":
            if "quarter_found" in self.flags:
                return "You have already harvested the fridge's one valuable asset: a quarter."
            self.flags.add("quarter_found")
            self.room_items[self.location].append("quarter")
            return (
                "You slide the fridge aside on its sticky casters. Beneath it: crumbs, a mystery "
                "hair, and a gleaming QUARTER. This building has not been cleaned since Y2K."
            )
        return f"You search the {thing or 'room'} and find only institutional regret."

    def _take(self, item: str) -> str:
        canonical = {
            "badge": "lanyard",
            "id": "lanyard",
            "employee badge": "lanyard",
        }.get(item, item)
        if canonical == "lanyard" and "drawer_open" not in self.flags:
            return "You don't see that here. The reception desk drawer is suspiciously closed."
        if canonical not in self.room_items.get(self.location, []):
            return f"You can't find any {item} here."
        self.room_items[self.location].remove(canonical)
        self.inventory.append(canonical)
        return f"Taken: {canonical}."

    def _wear(self, item: str) -> str:
        canonical = "insulated gloves" if item in {"gloves", "insulated gloves", "orange gloves"} else item
        if canonical not in self.inventory:
            return f"You don't have {canonical}."
        if canonical == "insulated gloves":
            self.flags.add("gloves_worn")
            return (
                "You put on the insulated gloves. They are orange, one size fits no one, "
                "and smell faintly of electrical confidence."
            )
        if canonical == "hoodie":
            self.flags.add("hoodie_worn")
            return (
                "You put on the hoodie. It says COLD STORAGE: WHY WAIT FOR THE CLOUD? "
                "Warmth is now a wearable feature."
            )
        return f"Wearing the {canonical} is less useful than you hoped."

    def _pull(self, target: str) -> str:
        if target not in {"blue cable", "blue wire"}:
            return f"You pull the {target or 'air'}. Nothing useful happens, but the gesture is cathartic."
        if self.location != "server_room":
            return "There is no blue alarm cable here."
        if "gloves_worn" not in self.flags:
            return (
                "You reach for the blue cable, but the warning tag says INSULATED GLOVES REQUIRED. "
                "The alarm increases its pitch in what might be laughter."
            )
        if "alarm" in self.completed_goals:
            return "The alarm is already silent. The quiet is somehow more judgmental."
        self.completed_goals.add("alarm")
        return (
            "You grip the blue cable and pull. The alarm cuts off mid-squawk. "
            "In the sudden silence, you can hear a distant ghost whisper, 'finally, silence'."
        )

    def _drop(self, item: str) -> str:
        if item not in self.inventory:
            return f"You don't have {item or 'that'} to drop."
        self.inventory.remove(item)
        self.room_items[self.location].append(item)
        if item == "hoodie":
            self.flags.discard("hoodie_worn")
        if item == "insulated gloves":
            self.flags.discard("gloves_worn")
        return f"Dropped: {item}. It joins the floor's growing collection of bad decisions."

    def _show_inventory(self) -> str:
        if not self.inventory:
            return "You are carrying nothing but unresolved incidents."
        return "You are carrying: " + ", ".join(self.inventory) + "."

    def _hint(self) -> str:
        if "lanyard" not in self.inventory:
            return (
                "HINT: The employee door needs an employee badge. The reception desk has a "
                "drawer, and the drawer has opinions about being closed."
            )
        if "hoodie" not in self.inventory and "hoodie_worn" not in self.flags:
            return "HINT: The reception coat rack has a hoodie. It might be cold where the key is kept."

        if "cooling" not in self.completed_goals:
            if "valve wheel" in self.inventory:
                return "HINT: Take the valve wheel to the mechanical room and use it on the coolant valve."
            if "valve wheel" in self.room_items.get("hallway", []):
                return "HINT: The vending machine delivered something useful. Take the valve wheel."
            if "quarter" in self.inventory:
                return (
                    "HINT: Selection B4 of the hallway vending machine sounds useful. "
                    "Try using the quarter on it."
                )
            if "vending_purchased" in self.flags:
                return "HINT: The valve wheel from the vending machine is now in the hallway."
            return "HINT: Cooling needs a valve wheel. The break room fridge is hiding loose change."

        if "alarm" not in self.completed_goals:
            if "insulated gloves" not in self.inventory and "gloves_worn" not in self.flags:
                return "HINT: The mechanical room toolbox contains insulated gloves."
            if "gloves_worn" not in self.flags:
                return "HINT: Wear the insulated gloves before touching the alarm cable."
            return "HINT: In the server room, pull the blue alarm cable. Not the red one. Never the red one."

        if "root" not in self.completed_goals:
            if "ghost_paid" in self.flags:
                return "HINT: The NOC terminal is waiting. Use it, then type the password Mortimer gave you."
            if "coffee" in self.inventory:
                return "HINT: The ghost in the hallway requested coffee. Try giving it to him."
            return (
                "HINT: Mortimer wants coffee. The break room has pods, a mug, and a coffee machine."
            )

        if "exit" not in self.completed_goals:
            if "exit key" not in self.inventory:
                return "HINT: Wear the hoodie, enter the cold aisle, and take the emergency exit key."
            return "HINT: Return to reception and use the exit key on the emergency exit."

        return "HINT: The exit is unlocked. Go south and try not to think about the retrospective."

    def _show_goals(self) -> str:
        labels = {
            "cooling": "cooling restored",
            "alarm": "alarm silenced",
            "root": "root access acquired",
            "exit": "emergency exit unlocked",
        }
        lines = ["ESCAPE CHECKLIST:"]
        for goal, label in labels.items():
            mark = "[X]" if goal in self.completed_goals else "[ ]"
            lines.append(f"  {mark} {label}")
        lines.append("Then head south through the emergency exit.")
        return "\n".join(lines)

    def _use_exit_key(self) -> str:
        if self.location != "reception":
            return "The emergency exit is back at reception, where the ficus can judge your departure."
        if "exit key" not in self.inventory:
            return "You need the emergency exit key."
        missing = [
            label
            for goal, label in (
                ("cooling", "COOLING RESTORED"),
                ("alarm", "ALARM SILENCED"),
                ("root", "ROOT ACCESS"),
            )
            if goal not in self.completed_goals
        ]
        if missing:
            return (
                "The key turns, but the emergency release refuses to budge. "
                "The panel lists unmet conditions: "
                + ", ".join(missing)
                + ". Try the GOALS command."
            )
        if "exit" not in self.completed_goals:
            self.completed_goals.add("exit")
            return (
                "You turn the emergency exit key. Three locks retract in sequence, "
                "each one making a sound like a manager closing a ticket. "
                "EMERGENCY EXIT UNLOCKED. Head south."
            )
        return "The emergency exit is already unlocked. South is doing its best to remain optional."

    def _try_to_escape(self) -> str:
        if "exit" not in self.completed_goals:
            return (
                "The emergency exit remains sealed. Its panel glows with the four stages of "
                "corporate approval. A laminated sign says: TRY 'GOALS'."
            )
        self.won = True
        return (
            "You shoulder the door open and escape into the parking lot.\n\n"
            "Behind you, the datacenter goes quiet. Ahead, the morning sky is the color of "
            "unpatched software. In your pocket, your phone buzzes with a calendar invite: "
            "'Post-Incident Retrospective (Mandatory).'\n\n"
            "You have escaped COLD STORAGE. For now.\n"
            "*** YOU WIN ***"
        )

    def _use(self, phrase: str) -> str:
        item, separator, target = phrase.partition(" on ")
        item = item.strip()
        target = target.strip()
        if not separator:
            if item in {"terminal", "console"}:
                return self._use_terminal()
            return "Try 'use <item> on <thing>', or use the terminal."

        if item == "quarter" and target in {"vending machine", "vending"}:
            return self._use_vending_machine()
        if item == "valve wheel" and target in {"coolant valve", "valve"}:
            return self._use_valve_wheel()
        if item == "coffee pod" and target in {"coffee maker", "coffee machine"}:
            return self._load_coffee_pod()
        if item == "mug" and target in {"coffee maker", "coffee machine"}:
            return self._brew_coffee()
        if item == "exit key" and target in {"emergency exit", "exit", "front door", "door"}:
            return self._use_exit_key()
        if item not in self.inventory:
            return f"You don't have a {item}."
        return f"The {item} does not seem useful on the {target}."

    def _use_vending_machine(self) -> str:
        if self.location != "hallway":
            return "There's no vending machine here."
        if "quarter" not in self.inventory:
            return "The vending machine wants a quarter. It is not moved by sincerity."
        self.inventory.remove("quarter")
        if "vending_purchased" in self.flags:
            return "The machine eats the quarter and says THANK YOU. The thank-you is not worth a quarter."
        self.flags.add("vending_purchased")
        self.room_items["hallway"].append("valve wheel")
        return (
            "The quarter goes in with a satisfying THUNK. Selection B4, "
            "'EMERGENCY VALVE WHEEL (SEASONAL),' clunks into the tray."
        )

    def _use_valve_wheel(self) -> str:
        if self.location != "mechanical_room":
            return "There's no coolant valve here."
        if "valve wheel" not in self.inventory:
            return "You don't have a valve wheel."
        self.inventory.remove("valve wheel")
        self.completed_goals.add("cooling")
        return (
            "You press the wheel onto the fitting and turn. The pipes shudder, burp, and begin "
            "moving coolant with the enthusiasm of a first-time marathoner. COOLING RESTORED."
        )

    def _load_coffee_pod(self) -> str:
        if self.location != "break_room":
            return "The coffee maker is in the break room."
        if "coffee pod" not in self.inventory:
            return "You don't have a coffee pod."
        self.inventory.remove("coffee pod")
        self.flags.add("coffee_pod_loaded")
        return (
            "You insert the pod. The machine makes a sound like a modem being told bad news. "
            "It is ready for a mug."
        )

    def _brew_coffee(self) -> str:
        if self.location != "break_room":
            return "The coffee maker is in the break room."
        if "mug" not in self.inventory:
            return "You don't have a mug."
        if "coffee_pod_loaded" not in self.flags:
            return "The machine wheezes emptily. It needs a coffee pod first."
        self.inventory.remove("mug")
        self.inventory.append("coffee")
        return (
            "The machine produces a mug of coffee so dark it casts its own shadow. "
            "A small OLED screen reads: BEANOLOGY COMPLETE."
        )

    def _talk(self, target: str) -> str:
        if target not in {"ghost", "mortimer", "mortimer cache"}:
            return f"You talk to the {target}. It does not have much to say."
        if self.location != "hallway":
            return "Mortimer is haunting the hallway. He is contractually obligated to stay there."
        if "ghost_paid" in self.flags:
            return (
                "Mortimer sips the memory of coffee. 'Use the NOC terminal. Type the password. "
                "Do not run `rm -rf`; it is not a personality test.'"
            )
        return (
            "MORTIMER CACHE, the translucent ghost of a sysadmin, blocks the corridor. "
            "He died waiting for a change ticket to close and now haunts this building as a "
            "middle-manager-shaped area of low pressure.\n\n"
            "'I require COFFEE,' he intones. 'Then I will share the root password. "
            "It has not changed since 1998. Neither has management.'"
        )

    def _give(self, phrase: str) -> str:
        item, separator, target = phrase.partition(" to ")
        item = item.strip()
        target = target.strip()
        if not separator:
            return "Give what to whom? Try 'give <item> to <person>'."
        if target not in {"ghost", "mortimer", "mortimer cache"}:
            return f"The {target} politely declines."
        if self.location != "hallway":
            return "Mortimer is in the hallway."
        if item != "coffee":
            return "Mortimer looks disappointed. He has very specific coffee needs."
        if "coffee" not in self.inventory:
            return "You don't have any coffee to give."
        self.inventory.remove("coffee")
        self.flags.add("ghost_paid")
        return (
            "Mortimer takes the coffee without touching it. 'Ah. The sacred bean.'\n\n"
            "'The root password is hunter2. If anyone asks, you found it in a config file.'\n\n"
            "He fades slightly, leaving behind the smell of ozone and unresolved pull requests."
        )

    def _use_terminal(self) -> str:
        if self.location != "noc":
            return "The nearest terminal is in the NOC, north of the hallway."
        if "root" in self.completed_goals:
            return "ROOT CONSOLE. The terminal awaits commands. It has never been this polite before."
        self.flags.add("terminal_accessed")
        return (
            "The terminal wakes with a green cursor and a prompt: PASSWORD: "
            "Perhaps a helpful ghost knows it."
        )

    def _type_password(self, password: str) -> str:
        if self.location != "noc" or "terminal_accessed" not in self.flags:
            return "You type into the air. The air denies your credentials."
        if password == "hunter2":
            self.completed_goals.add("root")
            return (
                "ACCESS GRANTED. ROOT ACCESS acquired. The terminal displays a cheerful message: "
                "YOU ARE NOW QUALIFIED TO FIX EVERYTHING. There is no undo button."
            )
        return "ACCESS DENIED. The terminal suggests you forgot the password, capitalized it wrong, or exist."
