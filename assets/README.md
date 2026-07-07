# Assets

Static game assets loaded by the [rendering](../rendering) layer at runtime.

| Folder     | Contents                                   | Loaded by                                          |
| ---------- | ------------------------------------------ | -------------------------------------------------- |
| `sprites/` | Character & object images (agents, items)  | [`SpriteManager`](../rendering/sprite_manager.py)  |
| `tiles/`   | Terrain / map tile images                  | [`SpriteManager`](../rendering/sprite_manager.py)  |
| `sounds/`  | Sound effects & music                      | (future audio manager)                             |
| `fonts/`   | UI fonts                                   | [`UI`](../rendering/ui.py)                          |

Each folder keeps a `.gitkeep` so the empty directory is tracked. Drop real
assets in and reference them by logical key from the rendering code.
