# 🏰 Medieval Village Simulation

A modular, agent-based **Medieval Village Simulation** built on the
[Mesa](https://mesa.readthedocs.io/) multi-agent framework, with a future
[Pygame](https://www.pygame.org/) rendering layer.

> **Status:** 🚧 Architecture skeleton. This repository currently contains the
> **project scaffolding only** — clean, documented placeholder classes,
> interfaces, and TODO markers. **No simulation logic, agent behavior, or AI is
> implemented yet.** The goal of this stage is a solid, extensible foundation.

---

## 📖 Description

The Medieval Village Simulation models an autonomous medieval settlement in
which heterogeneous agents — villagers, farmers, guards, merchants, miners,
lumberjacks, builders, and wildlife — live, work, trade, and interact within a
dynamic world featuring terrain, weather, seasons, and finite resources.

The architecture is designed around **Clean Architecture**, **SOLID**
principles, and **Model-Driven Engineering (MDE)** so that complex subsystems
(FSMs, behavior trees, pathfinding, economy, communication) can be added
incrementally without restructuring the codebase.

---

## 🎯 Objectives

- Provide a **production-ready, extensible skeleton** for a large simulation.
- Cleanly separate concerns: agents, world, AI, economy, communication,
  rendering, and simulation orchestration.
- Integrate the **Mesa** framework (`Model`, `Agent`, `MultiGrid`, scheduling).
- Prepare a decoupled **Pygame** rendering layer.
- Enable future **AI techniques** (FSM, Behavior Trees, GOAP, RL, Genetic
  Algorithms) behind stable interfaces.
- Support **event-driven communication** between agents.
- Lay the groundwork for **MDE** (UML models → generated code).

---

## 🗂️ Folder Structure

```text
sma_medieval_sim/
├── assets/               # Static game assets
│   ├── sprites/          #   Character & object sprites
│   ├── tiles/            #   Terrain / map tiles
│   ├── sounds/           #   Sound effects & music
│   └── fonts/            #   UI fonts
│
├── config/               # Configuration layer
│   ├── settings.py       #   Typed settings (pydantic, loaded from .env)
│   ├── constants.py      #   Immutable simulation constants
│   └── colors.py         #   Named RGB color palette
│
├── core/                 # Application core / composition root
│   ├── model.py          #   Mesa Model (central simulation state)
│   ├── engine.py         #   Game/simulation loop orchestrator
│   ├── bootstrap.py      #   Dependency wiring (composition root)
│   └── logger.py         #   Logging setup
│
├── world/                # The simulated environment
│   ├── world.py          #   World aggregate (owns map/terrain/climate)
│   ├── map.py            #   Spatial grid abstraction over Mesa's grid
│   ├── terrain.py        #   Terrain types & tiles
│   ├── weather.py        #   Weather system
│   ├── season.py         #   Seasonal cycle
│   └── resources.py      #   World resource nodes (trees, ore, ...)
│
├── agents/               # Mesa agents
│   ├── base_agent.py     #   Abstract BaseAgent (mesa.Agent)
│   ├── villager.py       #   Villager base
│   ├── farmer.py         #   ...role-specific villagers
│   ├── guard.py
│   ├── merchant.py
│   ├── miner.py
│   ├── lumberjack.py
│   ├── builder.py
│   ├── wolf.py           #   Wildlife (predator)
│   └── deer.py           #   Wildlife (prey)
│
├── ai/                   # Decision-making subsystems
│   ├── fsm/              #   Finite State Machines
│   │   ├── state.py
│   │   └── state_machine.py
│   ├── behaviors/        #   Reusable behaviors
│   │   ├── eat.py
│   │   ├── sleep.py
│   │   ├── work.py
│   │   ├── trade.py
│   │   └── patrol.py
│   └── pathfinding/      #   Navigation
│       └── astar.py
│
├── communication/        # Event-driven messaging (MAS)
│   ├── event_bus.py      #   Publish/subscribe bus
│   ├── events.py         #   Event types
│   ├── mailbox.py        #   Per-agent inbox/outbox
│   └── message.py        #   Agent message envelope (FIPA-style)
│
├── economy/              # Economic subsystem
│   ├── market.py         #   Marketplace / order matching
│   ├── inventory.py      #   Item storage
│   ├── prices.py         #   Pricing model
│   └── resources.py      #   Economic goods / resource types
│
├── buildings/            # Structures on the map
│   ├── building.py       #   Abstract BaseBuilding
│   ├── house.py
│   ├── farm.py
│   ├── mine.py
│   ├── market.py
│   └── blacksmith.py
│
├── rendering/            # Pygame presentation layer
│   ├── renderer.py       #   Main renderer
│   ├── camera.py         #   Viewport / pan / zoom
│   ├── sprite_manager.py #   Sprite loading & caching
│   └── ui.py             #   HUD / overlays
│
├── simulation/           # Orchestration & persistence
│   ├── scheduler.py      #   Agent activation strategy (Mesa AgentSet)
│   ├── statistics.py     #   Data collection & metrics
│   └── save_manager.py   #   Save / load simulation state
│
├── mde/                  # Model-Driven Engineering
│   ├── uml/              #   UML source models
│   ├── generated/        #   Generated code (git-ignored)
│   └── templates/        #   Code-generation templates
│
├── tests/                # Test suite
├── docs/                 # Documentation
├── main.py               # Application entry point
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── .env.example
└── LICENSE
```

---

## ⚙️ Installation

### Prerequisites

- **Python 3.12+**
- `pip` and `venv` (bundled with modern Python)

### 1. Clone the repository

```bash
git clone <repository-url> sma_medieval_sim
cd sma_medieval_sim
```

### 2. Create a virtual environment

> The virtual environment is intentionally **not** committed. Create it locally.

```bash
# Linux / macOS
python3.12 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip

# Runtime dependencies
pip install -r requirements.txt

# ...or install the project (with dev tooling) in editable mode
pip install -e ".[dev]"
```

### 4. Configure the environment

```bash
cp .env.example .env
# Edit .env to taste (grid size, seed, rendering options, ...).
```

---

## ▶️ Running the Project

```bash
python main.py
```

> At this stage `main.py` only bootstraps and validates the skeleton (it wires
> the composition root and logs that initialization succeeded). The full
> simulation loop is not yet implemented.

---

## 🧱 Planned Architecture

The system follows a layered, dependency-inverted design:

```text
        ┌─────────────────────────────────────────────┐
        │                   main.py                    │
        └───────────────────────┬─────────────────────┘
                                 │  bootstrap (DI)
        ┌───────────────────────▼─────────────────────┐
        │                    core/                     │
        │   GameModel (Mesa) · Engine · Logger         │
        └───┬───────────┬───────────┬───────────┬──────┘
            │           │           │           │
     ┌──────▼───┐ ┌─────▼────┐ ┌────▼─────┐ ┌───▼───────┐
     │  world/  │ │ agents/  │ │   ai/    │ │ economy/  │
     └──────────┘ └────┬─────┘ └──────────┘ └───────────┘
                       │ publish/subscribe
                 ┌─────▼──────────┐
                 │ communication/ │
                 └────────────────┘

     rendering/ observes the model (read-only) via Pygame.
     simulation/ orchestrates scheduling, statistics & persistence.
```

**Key design decisions**

- **Mesa** owns the agent lifecycle, spatial grid, and data collection.
- **Agents depend on interfaces** (behaviors, pathfinding, state machines), not
  concrete strategies — new AI approaches plug in without touching agents.
- **Communication is decoupled** through an event bus and per-agent mailboxes.
- **Rendering is a read-only observer** of the model — the simulation runs
  headless (great for tests and batch experiments) or with Pygame.
- **Configuration is centralized** and validated with pydantic.

---

## 🗺️ Future Roadmap

| Phase | Focus                                                                    |
| ----- | ------------------------------------------------------------------------ |
| 0     | ✅ Architecture skeleton (this stage)                                     |
| 1     | Mesa `Model` + `MultiGrid` + scheduler; basic step loop (headless)       |
| 2     | Base agents & needs; simple FSM-driven behavior                          |
| 3     | World systems: terrain, resources, seasons, weather                      |
| 4     | Economy: inventory, market, prices, trading                              |
| 5     | Communication: event bus, mailboxes, agent negotiation                   |
| 6     | Pathfinding (A\*) and navigation                                         |
| 7     | Pygame rendering, camera, sprites, HUD                                    |
| 8     | Persistence (save/load) and statistics/metrics                           |
| 9     | Advanced AI: Behavior Trees, GOAP, Reinforcement Learning, GAs           |
| 10    | MDE pipeline: UML models → generated code                                |

---

## 🤝 Contributing

This is an architectural foundation. When implementing a subsystem, keep the
existing module boundaries, add type hints and docstrings, and cover new logic
with tests under `tests/`.

## 📄 License

Released under the [MIT License](LICENSE).
