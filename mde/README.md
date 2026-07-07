# Model-Driven Engineering (MDE)

This directory reserves the structure for a future **model-to-code** pipeline.

## Layout

| Folder        | Purpose                                                        |
| ------------- | ------------------------------------------------------------- |
| `uml/`        | Source models (UML class/state diagrams, e.g. `.uml`, `.xmi`).|
| `templates/`  | Code-generation templates (e.g. Jinja2).                      |
| `generated/`  | Generated output. **Git-ignored** — never edit by hand.       |

## Intended pipeline (future work)

```text
uml/*.uml  ──parse──▶  intermediate model  ──render(templates/)──▶  generated/
```

## Guidelines

- Treat `generated/` as disposable; regenerate rather than edit.
- Keep hand-written code and generated code in separate modules to avoid
  merge conflicts (generation-gap pattern).

> Not implemented yet — this is architectural scaffolding only.
