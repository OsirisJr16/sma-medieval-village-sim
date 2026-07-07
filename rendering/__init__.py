"""Rendering package (Pygame).

The presentation layer. It is a *read-only observer* of the simulation model:
the :class:`rendering.renderer.Renderer` draws the current world state each
frame, the :class:`rendering.camera.Camera` controls the viewport, the
:class:`rendering.sprite_manager.SpriteManager` supplies images, and
:class:`rendering.ui.UI` draws overlays. Because rendering never mutates the
model, the simulation can also run fully headless.

Pygame is imported lazily inside implementations so headless runs (and tests)
need no display.
"""
