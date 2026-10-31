# Cold Storage: The Haunted Data Center Escape

> **About this repo:** this game was written by DeepSeek V4.1 Flash on Ollama Cloud, driven by the Codex desktop app with Ollama as the bridge. It came from a single prompt (at the end of this README) in about three minutes. It's one of three runs of the same prompt: [COLD STORAGE](https://mrfuture.com/projects/cold-storage/) (Qwen3.8 27B on a 96GB MacBook Pro M3 Max, through the Pi coding agent; [repo](https://github.com/BillDX/coldstorage)) and [MuchColderStorage](https://github.com/BillDX/MuchColderStorage) (gpt-oss-20b, local, through Codex and Ollama). The write-up comparing all three: [Codex + Ollama: an easier route to coding with local LLMs](https://mrfuture.com/2026/10/codex-ollama-local-llms/). Apart from this note and "The prompt" section, everything here is the model's output, unedited.

A standalone, Infocom-style text adventure about surviving the graveyard shift.

You arrived at 3:13 AM to reboot one NAS. Now the doors are sealed, cooling is
down, the alarm has opinions, and a ghost is enforcing a change freeze. Escape
requires four goals:

- Restore cooling
- Silence the alarm
- Obtain root access
- Unlock the emergency exit

The puzzles are logical, the inventory matters, and the ghost has very specific
coffee needs.

## Run it

Requires Python 3.10 or newer. There are no third-party dependencies.

```bash
python3 -m cold_storage
```

Type `help` in game for commands, `goals` for the escape checklist, and `hint`
for a contextual nudge. Directions work as `north`, `south`, `east`, `west`, or
`n`, `s`, `e`, `w`.

## Test it

The project uses only the standard-library `unittest` runner.

```bash
python3 -m unittest discover -s tests -v
```

The suite contains focused unit tests for parser/state behavior and two full
playthrough tests: one through the real game engine and one through the actual
`python3 -m cold_storage` command-line entry point.

Development followed strict red/green TDD: each behavior got a failing test
first, then only enough implementation to pass, followed by refactoring with the
suite kept green.

## A small sample

```text
> look
THE PALE CORRIDOR. A VENDING MACHINE glows with stale snacks...
MORTIMER CACHE, a translucent sysadmin ghost, hovers beside it...

> talk to ghost
'I require COFFEE... Then I will share the root password.
It has not changed since 1998. Neither has management.'
```

## Full walkthrough (major spoilers)

<details>
<summary>Click to reveal the command sequence used by the playthrough test</summary>

```text
take hoodie
wear hoodie
open drawer
take lanyard
north
east
search fridge
take quarter
take coffee pod
take mug
use coffee pod on coffee maker
use mug on coffee maker
west
give coffee to ghost
north
use terminal
type hunter2
south
east
north
open toolbox
take insulated gloves
south
west
use quarter on vending machine
take valve wheel
east
north
use valve wheel on coolant valve
south
west
west
wear insulated gloves
pull blue cable
north
take exit key
south
east
south
use exit key on emergency exit
goals
south
```

</details>

## The prompt

> lets make a fun/funny standalone text adventure game, similar to an infocom adventure, about escaping from a haunted data center. writing it in python seems reasonable. It should have inventory, clever puzzles, humorous descriptions, and multiple goals needed to be able to escape the data center as the main goal. It should be solvable, and the solutions should be fairly logical. But the most important thing is to make it very fun. while coding make sure we use red/green style testing both for unit testing and for overall playthrough testing.
