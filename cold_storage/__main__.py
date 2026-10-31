"""Interactive command-line entry point for Cold Storage."""

from __future__ import annotations

from .game import Game


TITLE = r"""
   ______      ____  ____        _____ __                 __
  / ____/___  / __ \/ __ \      / ___// /_____  _________/ /___ _
 / /   / __ \/ / / / / / /______\__ \/ __/ __ \/ ___/ __  / __ `/
/ /___/ /_/ / /_/ / /_/ /_____/__/ / /_/ /_/ / /  / /_/ / /_/ /
\____/\____/_____/_____/     /____/\__/\____/_/   \__,_/\__,_/

             THE HAUNTED DATA CENTER ESCAPE
"""

INTRO = """
It is 3:13 AM. You came in to reboot one NAS.
The building has other plans.

The doors have sealed. The cooling has stopped. The alarm has opinions.
Somewhere in the racks, a ghost is enforcing a change freeze.

Find a way out. Restore cooling, silence the alarm, get root, and unlock
the emergency exit. Four goals stand between you and the parking lot.

Useful commands:
  look, examine <thing>, take <thing>, inventory, use <thing> on <thing>
  wear <thing>, search <thing>, talk to ghost, goals, help, quit

Directions: north/south/east/west (or n/s/e/w)
"""

HELP = """
COMMANDS
  look / l                 Describe where you are
  examine / x <thing>      Look closely at something
  take / get <thing>       Put something in your inventory
  inventory / i            List what you are carrying
  wear <thing>             Put on wearable equipment
  search <thing>           Search a suspicious object
  use <thing> on <thing>   Try the obvious interaction
  give <thing> to <person> Make a socially awkward trade
  drop <thing>             Return an item to the room
  pull <thing>             Pull something that probably has a warning label
  talk to ghost            Consult local management
  goals                    Show the escape checklist
  hint                     Get a nudge without the full answer
  quit                     Abandon your colleagues (and the game)
  restart                  Start over
"""


def main() -> int:
    game = Game()
    print(TITLE)
    print(INTRO)
    print(game.execute("look"))

    while not game.won:
        try:
            command = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nThe datacenter keeps you. For now.")
            return 0

        normalized = command.strip().lower()
        if normalized in {"quit", "exit", "q"}:
            print("You leave the datacenter to its haunting. The ghost calls it a lateral move.")
            return 0
        if normalized == "restart":
            game = Game()
            print("\n" + "=" * 70)
            print(INTRO)
            print(game.execute("look"))
            continue
        if normalized in {"help", "?"}:
            print(HELP)
            continue

        print("\n" + game.execute(command))

    print("\nThanks for playing. Please complete the mandatory post-incident survey.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
