"""Economy package.

Models the village economy: tradable goods (:mod:`economy.resources`), agent
:mod:`economy.inventory`, a :mod:`economy.market` where trades are matched, and
a :mod:`economy.prices` model that determines value. Kept independent of any
single agent so multiple agents share one consistent economic world.
"""
