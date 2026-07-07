# Architecture

This document describes the intended architecture of the Medieval Village
Simulation. The repository currently contains the **skeleton** for this design.

## Guiding principles

- **Clean Architecture** — dependencies point inward. Domain packages
  (`world`, `agents`, `economy`, `ai`) do not depend on `rendering` or on the
  `core` composition root.
- **SOLID** — small, single-purpose classes behind interfaces; new strategies
  (AI techniques, pathfinders, pricing) plug in via abstractions.
- **Headless-first** — the simulation runs without a display; `rendering` is an
  optional, read-only observer. This keeps the model testable and batchable.
- **Explicit composition** — objects are wired in one place
  ([core/bootstrap.py](../core/bootstrap.py)), not via hidden globals.

## Layers

| Layer            | Packages                                             | Depends on            |
| ---------------- | ---------------------------------------------------- | --------------------- |
| Configuration    | `config`                                             | — (leaf)              |
| Domain           | `world`, `agents`, `ai`, `economy`, `buildings`, `communication` | `config`  |
| Orchestration    | `simulation`                                         | domain, `config`      |
| Application core | `core`                                               | domain, `simulation`  |
| Presentation     | `rendering`                                          | reads `core.model`    |
| Entry point      | `main.py`                                            | `core`                |

> Rule of thumb: an arrow may point toward more abstract/stable layers, never
> away from them. Presentation reads the model but never mutates it.

## Runtime flow (planned)

```text
main.py
  └─ core.bootstrap.bootstrap()      # construct + wire the object graph
       ├─ config.settings            # load & validate configuration
       ├─ core.model.GameModel       # Mesa model owns grid + agents + world
       ├─ world.World                # terrain, weather, season, resources
       └─ core.engine.Engine         # main loop
            └─ per tick:
                 model.step()        # world.step() -> scheduler.step() -> stats
                 renderer.render()   # optional, read-only
```

## Key extension points

| Want to add…            | Implement…                                                        |
| ----------------------- | ----------------------------------------------------------------- |
| A new agent role        | Subclass [`Villager`](../agents/villager.py) (or `BaseAgent`).    |
| A new behavior          | Subclass [`Behavior`](../ai/behaviors/__init__.py).               |
| A new AI technique      | Add a sibling subpackage under `ai/` (e.g. `ai/goap`, `ai/rl`).   |
| A new pathfinder        | Implement [`Pathfinder`](../ai/pathfinding/astar.py).             |
| A new building          | Subclass [`BaseBuilding`](../buildings/building.py).              |
| A new tradable good     | Add to [`ResourceType`](../economy/resources.py).                 |
| A new event             | Add to [`EventType`](../communication/events.py).                 |
| A new activation order  | Extend [`ActivationOrder`](../simulation/scheduler.py).           |

## Mesa notes

- Targets **Mesa 3.x**. `mesa.Agent` auto-assigns `unique_id` and registers with
  `model.agents`; the legacy `mesa.time` schedulers are not used.
- Activation order is centralized in
  [`simulation/scheduler.py`](../simulation/scheduler.py), which wraps
  `model.agents` AgentSet methods (`do` / `shuffle_do`).

## Status

Skeleton only. See the roadmap in the [README](../README.md) for the
implementation phases.
