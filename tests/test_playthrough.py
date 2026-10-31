import subprocess
import sys
import unittest
from pathlib import Path

from cold_storage.game import Game


SOLUTION_COMMANDS = [
    "take hoodie",
    "wear hoodie",
    "open drawer",
    "take lanyard",
    "north",
    "east",
    "search fridge",
    "take quarter",
    "take coffee pod",
    "take mug",
    "use coffee pod on coffee maker",
    "use mug on coffee maker",
    "west",
    "give coffee to ghost",
    "north",
    "use terminal",
    "type hunter2",
    "south",
    "east",
    "north",
    "open toolbox",
    "take insulated gloves",
    "south",
    "west",
    "use quarter on vending machine",
    "take valve wheel",
    "east",
    "north",
    "use valve wheel on coolant valve",
    "south",
    "west",
    "west",
    "wear insulated gloves",
    "pull blue cable",
    "north",
    "take exit key",
    "south",
    "east",
    "south",
    "use exit key on emergency exit",
    "goals",
    "south",
]


class FullPlaythroughTests(unittest.TestCase):
    def test_real_game_reaches_victory_with_all_goals_complete(self):
        game = Game()

        messages = [game.execute(command) for command in SOLUTION_COMMANDS]

        self.assertTrue(game.won)
        self.assertEqual(
            game.completed_goals,
            {"cooling", "alarm", "root", "exit"},
        )
        self.assertIn("YOU WIN", messages[-1])


class StandaloneEntryPointTests(unittest.TestCase):
    def test_module_playthrough_prints_victory(self):
        project_root = Path(__file__).resolve().parents[1]
        scripted_input = "\n".join(SOLUTION_COMMANDS + ["quit"]) + "\n"

        result = subprocess.run(
            [sys.executable, "-m", "cold_storage"],
            cwd=project_root,
            input=scripted_input,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("YOU WIN", result.stdout)
        self.assertIn("root access acquired", result.stdout.lower())
