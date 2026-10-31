import unittest

from cold_storage.game import Game


class NewGameTests(unittest.TestCase):
    def test_new_game_starts_in_reception(self):
        game = Game()

        self.assertEqual(game.location, "reception")


if __name__ == "__main__":
    unittest.main()


class MovementAndInventoryTests(unittest.TestCase):
    def test_moving_north_without_lanyard_is_blocked(self):
        game = Game()

        message = game.execute("north")

        self.assertEqual(game.location, "reception")
        self.assertIn("lanyard", message.lower())

    def test_taking_visible_item_moves_it_to_inventory(self):
        game = Game()
        game.execute("open drawer")

        game.execute("take lanyard")

        self.assertIn("lanyard", game.inventory)
        self.assertNotIn("lanyard", game.items_at("reception"))

    def test_north_with_lanyard_enters_hallway(self):
        game = Game()
        game.execute("open drawer")
        game.execute("take lanyard")

        game.execute("north")

        self.assertEqual(game.location, "hallway")

    def test_inventory_command_names_carried_items(self):
        game = Game()
        game.execute("open drawer")
        game.execute("take lanyard")

        message = game.execute("inventory")

        self.assertIn("lanyard", message)


class CoolingPuzzleTests(unittest.TestCase):
    def _enter_hallway(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

    def test_hallway_east_enters_break_room(self):
        game = Game()
        self._enter_hallway(game)

        game.execute("east")

        self.assertEqual(game.location, "break_room")

    def test_searching_fridge_reveals_quarter(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")

        message = game.execute("search fridge")
        game.execute("take quarter")

        self.assertIn("quarter", message.lower())
        self.assertIn("quarter", game.inventory)

    def test_quarter_buys_valve_wheel_from_vending_machine(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")
        game.execute("search fridge")
        game.execute("take quarter")
        game.execute("west")

        message = game.execute("use quarter on vending machine")
        game.execute("take valve wheel")

        self.assertNotIn("quarter", game.inventory)
        self.assertIn("valve wheel", game.inventory)
        self.assertIn("thunk", message.lower())

    def test_using_valve_wheel_on_coolant_valve_restores_cooling(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")
        game.execute("search fridge")
        game.execute("take quarter")
        game.execute("west")
        game.execute("use quarter on vending machine")
        game.execute("take valve wheel")
        game.execute("east")
        game.execute("north")

        message = game.execute("use valve wheel on coolant valve")

        self.assertEqual(game.location, "mechanical_room")
        self.assertIn("cooling", message.lower())
        self.assertIn("cooling", game.completed_goals)


class CoffeeAndRootTests(unittest.TestCase):
    def _enter_hallway(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

    def _brew_coffee(self, game):
        self._enter_hallway(game)
        game.execute("east")
        game.execute("take coffee pod")
        game.execute("take mug")
        game.execute("use coffee pod on coffee maker")
        game.execute("use mug on coffee maker")

    def test_brewing_coffee_puts_hot_coffee_in_inventory(self):
        game = Game()
        self._brew_coffee(game)

        self.assertIn("coffee", game.inventory)

    def test_talking_to_ghost_requests_coffee(self):
        game = Game()
        self._enter_hallway(game)

        message = game.execute("talk to ghost")

        self.assertIn("coffee", message.lower())

    def test_giving_coffee_to_ghost_reveals_root_password(self):
        game = Game()
        self._brew_coffee(game)
        game.execute("west")

        message = game.execute("give coffee to ghost")

        self.assertIn("hunter2", message.lower())
        self.assertNotIn("coffee", game.inventory)

    def test_root_terminal_accepts_password_from_ghost(self):
        game = Game()
        self._brew_coffee(game)
        game.execute("west")
        game.execute("give coffee to ghost")
        game.execute("north")
        game.execute("use terminal")

        message = game.execute("type hunter2")

        self.assertIn("root", message.lower())
        self.assertIn("root", game.completed_goals)

    def test_root_terminal_rejects_wrong_password(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("north")
        game.execute("use terminal")

        message = game.execute("type swordfish")

        self.assertIn("denied", message.lower())
        self.assertNotIn("root", game.completed_goals)


class AlarmPuzzleTests(unittest.TestCase):
    def _enter_hallway(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

    def _get_gloves(self, game):
        self._enter_hallway(game)
        game.execute("east")
        game.execute("north")
        game.execute("open toolbox")
        game.execute("take insulated gloves")
        game.execute("south")
        game.execute("west")

    def test_alarm_panel_clue_names_the_blue_cable(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("west")

        message = game.execute("examine alarm panel")

        self.assertIn("blue cable", message.lower())

    def test_toolbox_contains_insulated_gloves(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")
        game.execute("north")

        game.execute("open toolbox")
        game.execute("take insulated gloves")

        self.assertIn("insulated gloves", game.inventory)

    def test_pulling_alarm_cable_without_gloves_is_blocked(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("west")

        message = game.execute("pull blue cable")

        self.assertIn("gloves", message.lower())
        self.assertNotIn("alarm", game.completed_goals)

    def test_pulling_alarm_cable_with_worn_gloves_silences_alarm(self):
        game = Game()
        self._get_gloves(game)
        game.execute("wear insulated gloves")
        game.execute("west")

        message = game.execute("pull blue cable")

        self.assertEqual(game.location, "server_room")
        self.assertIn("silence", message.lower())
        self.assertIn("alarm", game.completed_goals)


class ColdAisleTests(unittest.TestCase):
    def _reach_server_room(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")
        game.execute("west")

    def test_server_room_north_without_hoodie_is_too_cold(self):
        game = Game()
        self._reach_server_room(game)

        message = game.execute("north")

        self.assertEqual(game.location, "server_room")
        self.assertIn("cold", message.lower())

    def test_wearing_hoodie_allows_entry_to_cold_aisle(self):
        game = Game()
        game.execute("take hoodie")
        game.execute("wear hoodie")
        self._reach_server_room(game)

        game.execute("north")

        self.assertEqual(game.location, "cold_aisle")

    def test_emergency_exit_key_can_be_taken_from_cold_aisle(self):
        game = Game()
        game.execute("take hoodie")
        game.execute("wear hoodie")
        self._reach_server_room(game)
        game.execute("north")

        game.execute("take exit key")

        self.assertIn("exit key", game.inventory)


class EscapeTests(unittest.TestCase):
    def test_goals_command_lists_all_four_objectives(self):
        game = Game()

        message = game.execute("goals").lower()

        for objective in ("cooling", "alarm", "root", "exit"):
            self.assertIn(objective, message)

    def test_exit_key_is_rejected_until_system_requirements_are_met(self):
        game = Game()
        game.inventory.append("exit key")

        message = game.execute("use exit key on emergency exit")

        self.assertIn("cooling", message.lower())
        self.assertNotIn("exit", game.completed_goals)

    def test_unlocked_exit_then_south_wins_the_game(self):
        game = Game()
        game.completed_goals.update({"cooling", "alarm", "root"})
        game.inventory.append("exit key")
        game.execute("use exit key on emergency exit")

        message = game.execute("south")

        self.assertTrue(game.won)
        self.assertIn("escape", message.lower())


class DiscoverabilityTests(unittest.TestCase):
    def _enter_hallway(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

    def test_reception_look_points_to_drawer_hoodie_and_exit(self):
        game = Game()

        message = game.execute("look").lower()

        for clue in ("drawer", "hoodie", "exit"):
            self.assertIn(clue, message)

    def test_hallway_look_names_ghost_and_vending_machine(self):
        game = Game()
        self._enter_hallway(game)

        message = game.execute("look").lower()

        self.assertIn("ghost", message)
        self.assertIn("vending machine", message)

    def test_examining_vending_machine_advertises_valve_wheel(self):
        game = Game()
        self._enter_hallway(game)

        message = game.execute("examine vending machine").lower()

        self.assertIn("valve wheel", message)

    def test_break_room_look_names_coffee_supplies(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")

        message = game.execute("look").lower()

        for clue in ("fridge", "coffee pod", "mug"):
            self.assertIn(clue, message)

    def test_server_room_look_names_alarm_panel_and_blue_cable(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("west")

        message = game.execute("look").lower()

        self.assertIn("alarm panel", message)
        self.assertIn("blue cable", message)

    def test_cold_aisle_look_names_exit_key(self):
        game = Game()
        game.execute("take hoodie")
        game.execute("wear hoodie")
        self._enter_hallway(game)
        game.execute("west")
        game.execute("north")

        message = game.execute("look").lower()

        self.assertIn("exit key", message)


class DiscoverabilityTests(unittest.TestCase):
    def _enter_hallway(self, game):
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

    def test_reception_look_names_drawer_hoodie_and_exit(self):
        game = Game()

        message = game.execute("look").lower()

        for clue in ("drawer", "hoodie", "exit"):
            self.assertIn(clue, message)

    def test_hallway_look_names_ghost_and_vending_machine(self):
        game = Game()
        self._enter_hallway(game)

        message = game.execute("look").lower()

        self.assertIn("ghost", message)
        self.assertIn("vending machine", message)

    def test_vending_machine_examine_advertises_valve_wheel(self):
        game = Game()
        self._enter_hallway(game)

        message = game.execute("examine vending machine").lower()

        self.assertIn("valve wheel", message)

    def test_break_room_look_names_coffee_pod_and_mug(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("east")

        message = game.execute("look").lower()

        self.assertIn("coffee pod", message)
        self.assertIn("mug", message)

    def test_server_room_look_names_alarm_panel_cable_and_cold_aisle(self):
        game = Game()
        self._enter_hallway(game)
        game.execute("west")

        message = game.execute("look").lower()

        self.assertIn("alarm panel", message)
        self.assertIn("blue cable", message)
        self.assertIn("cold aisle", message)

    def test_cold_aisle_look_names_exit_key(self):
        game = Game()
        game.execute("take hoodie")
        game.execute("wear hoodie")
        self._enter_hallway(game)
        game.execute("west")
        game.execute("north")

        message = game.execute("look").lower()

        self.assertIn("exit key", message)


class PolishTests(unittest.TestCase):
    def test_drop_returns_item_from_inventory_to_current_room(self):
        game = Game()
        game.execute("take hoodie")

        game.execute("drop hoodie")

        self.assertNotIn("hoodie", game.inventory)
        self.assertIn("hoodie", game.items_at("reception"))

    def test_early_hint_points_toward_reception_desk(self):
        game = Game()

        message = game.execute("hint").lower()

        self.assertIn("drawer", message)

    def test_cooling_hint_points_toward_fridge_when_quarter_is_missing(self):
        game = Game()
        game.execute("take hoodie")
        game.execute("wear hoodie")
        game.execute("open drawer")
        game.execute("take lanyard")
        game.execute("north")

        message = game.execute("hint").lower()

        self.assertIn("fridge", message)

    def test_sudo_is_refused_with_in_character_message(self):
        game = Game()

        message = game.execute("sudo make me a sandwich")

        self.assertIn("sudoers", message.lower())
