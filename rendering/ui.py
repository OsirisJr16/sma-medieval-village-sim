"""Heads-up display / UI overlays.

:class:`UI` draws a stats dashboard over the world view: a clock with a
day/night bar, a population history graph (linear or log scale), per-species
state breakdowns, an inspector for a selected agent, and a controls/status
footer. Like the rest of the rendering layer it only reads from the model; the
small history buffer it keeps is presentation state, not simulation state.

Pygame is imported lazily so importing this module needs no display.
"""

from __future__ import annotations

import math
from collections import Counter, deque
from typing import TYPE_CHECKING, Any

from agents.needs import Need
from agents.perception import nearest_of_type
from config.colors import GUARD_COLOR, RGB, UI_ACCENT, UI_FOREGROUND
from config.constants import AgentType
from economy.resources import ResourceType

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent
    from core.model import GameModel

    Surface = Any

# Per-species display color (distinct and legible on the dark panel).
_VILLAGER: RGB = (226, 190, 120)
_GUARD: RGB = (120, 150, 230)
_FARMER: RGB = (168, 200, 96)
_DEER: RGB = (120, 196, 116)
_WOLF: RGB = (216, 96, 96)

# Sections: (label, agent type, color), drawn top to bottom. Guards and farmers
# are villager roles, folded into the Villagers section — their work shows up as
# the "defending" / "farming" states rather than as separate populations.
_SECTIONS: tuple[tuple[str, AgentType, RGB], ...] = (
    ("Villagers", AgentType.VILLAGER, _VILLAGER),
    ("Deer", AgentType.DEER, _DEER),
    ("Wolves", AgentType.WOLF, _WOLF),
)
# Fold these agent types into another for tallying.
_MERGE: dict[AgentType, AgentType] = {
    AgentType.GUARD: AgentType.VILLAGER,
    AgentType.FARMER: AgentType.VILLAGER,
}
# Inspector header color per agent type (roles keep their own color).
_COLOR_OF: dict[AgentType, RGB] = {
    AgentType.VILLAGER: _VILLAGER,
    AgentType.GUARD: _GUARD,
    AgentType.FARMER: _FARMER,
    AgentType.DEER: _DEER,
    AgentType.WOLF: _WOLF,
}

# Semantic color per activity, shared across species.
_STATE_COLORS: dict[str, RGB] = {
    "working": (120, 172, 96),
    "farming": (168, 200, 96),
    "trading": (216, 178, 92),
    "wandering": (150, 178, 112),
    "prowling": (150, 150, 162),
    "eating": (224, 182, 74),
    "grazing": (126, 192, 116),
    "sleeping": (96, 126, 206),
    "fleeing": (226, 138, 72),
    "alarmed": (232, 96, 84),
    "defending": (120, 150, 230),
    "hunting": (214, 84, 84),
}
_DEFAULT_STATE_COLOR: RGB = (150, 150, 160)

# Which predator each prey type flees, and vice versa, for the inspector.
_TARGETS: dict[AgentType, tuple[str, AgentType]] = {
    AgentType.WOLF: ("prey", AgentType.DEER),
    AgentType.DEER: ("threat", AgentType.WOLF),
}

_PANEL_BG: RGB = (24, 26, 34)
_CARD_BG: RGB = (32, 35, 45)
_MUTED: RGB = (168, 174, 188)
_GRAPH_BG: RGB = (18, 20, 27)
_HUNGER_BAR: RGB = (214, 96, 86)
_ENERGY_BAR: RGB = (120, 186, 110)
_HP_BAR: RGB = (206, 172, 84)
# Reference max hit points per agent kind, for the inspector's HP bar.
_HP_MAX: dict[AgentType, float] = {
    AgentType.VILLAGER: 45.0,
    AgentType.FARMER: 45.0,
    AgentType.MERCHANT: 45.0,
    AgentType.GUARD: 120.0,
    AgentType.WOLF: 100.0,
}
_HISTORY_LEN = 200


class UI:
    """Renders the stats dashboard sidebar.

    Attributes:
        width: Sidebar width in pixels.
        log_scale: Whether the history graph uses a logarithmic y-axis.
    """

    def __init__(self, width: int = 280) -> None:
        """Initialize the UI layer.

        Args:
            width: Sidebar width in pixels.
        """
        self.width: int = width
        self.log_scale: bool = True
        self._history: dict[AgentType, deque[int]] = {
            kind: deque(maxlen=_HISTORY_LEN) for _, kind, _ in _SECTIONS
        }
        self._last_sample: int = -1
        self._title_font: Any = None
        self._head_font: Any = None
        self._body_font: Any = None
        self._small_font: Any = None

    def toggle_scale(self) -> None:
        """Switch the history graph between logarithmic and linear scale."""
        self.log_scale = not self.log_scale

    def draw(
        self,
        surface: Surface,
        model: GameModel,
        x: int,
        *,
        selected: BaseAgent | None = None,
        paused: bool = False,
        sim_fps: int = 0,
    ) -> None:
        """Draw the dashboard onto ``surface`` starting at column ``x``.

        Args:
            surface: The target surface.
            model: The simulation model to read stats from (read-only).
            x: Left edge of the sidebar, in pixels.
            selected: The agent to inspect, if any.
            paused: Whether the simulation is paused.
            sim_fps: Current simulation speed in steps per second.
        """
        import pygame

        self._ensure_fonts()
        pygame.draw.rect(surface, _PANEL_BG, (x, 0, self.width, surface.get_height()))

        breakdown, roles, gold = self._collect(model)
        self._sample_history(model, breakdown)
        villager_states = breakdown.get(AgentType.VILLAGER, Counter())
        under_attack = villager_states["defending"] + villager_states["alarmed"] > 0

        pad = 16
        ix = x + pad
        iw = self.width - pad * 2
        y = pad
        y = self._draw_header(surface, model, ix, iw, y) + 8
        if under_attack:
            y = self._draw_alert(surface, ix, iw, y) + 8
        y = self._draw_graph(surface, ix, iw, y) + 4
        y = self._draw_vitals(surface, model, ix, iw, y) + 12

        for label, kind, color in _SECTIONS:
            states = breakdown.get(kind, Counter())
            y = self._draw_card(surface, ix, iw, y, label, color, states)
            if kind is AgentType.VILLAGER:
                y = self._draw_roles(surface, ix, iw, y + 2, roles)
            y += 10

        if selected is not None:
            self._draw_inspector(surface, ix, iw, y, selected, model)
        self._draw_footer(surface, ix, iw, surface.get_height(), paused, sim_fps, model, gold)

    # --- Header ---------------------------------------------------------------

    def _draw_header(
        self, surface: Surface, model: GameModel, x: int, w: int, y: int
    ) -> int:
        import pygame

        clock = model.clock
        title = self._title_font.render("Medieval Village", True, UI_FOREGROUND)
        surface.blit(title, (x, y))
        y += title.get_height() + 6

        stamp = f"{clock.season.current.value.title()} · Day {clock.day + 1}"
        surface.blit(self._body_font.render(stamp, True, UI_ACCENT), (x, y))
        time_surf = self._body_font.render(f"{clock.hour:02d}:00", True, UI_ACCENT)
        surface.blit(time_surf, (x + w - time_surf.get_width(), y))
        y += time_surf.get_height() + 6

        bar_h = 6
        pygame.draw.rect(surface, _GRAPH_BG, (x, y, w, bar_h), border_radius=3)
        lit = round(w * clock.daylight)
        if lit > 0:
            tint = (150, 150, 170) if clock.is_night else (238, 205, 120)
            pygame.draw.rect(surface, tint, (x, y, lit, bar_h), border_radius=3)
        y += bar_h + 4

        # Forage: average grass across the pasture (seasonal food abundance).
        pygame.draw.rect(surface, _GRAPH_BG, (x, y, w, bar_h), border_radius=3)
        grass = round(w * model.pasture.average())
        if grass > 0:
            pygame.draw.rect(surface, (110, 168, 92), (x, y, grass, bar_h), border_radius=3)
        y += bar_h + 4

        # Granary: the village food store farmers stock and everyone eats from.
        pygame.draw.rect(surface, _GRAPH_BG, (x, y, w, bar_h), border_radius=3)
        fill = round(w * min(1.0, model.granary / max(1.0, model.granary_capacity)))
        if fill > 0:
            pygame.draw.rect(surface, (214, 176, 90), (x, y, fill, bar_h), border_radius=3)
        return y + bar_h

    # --- Population history graph ---------------------------------------------

    def _sample_history(
        self, model: GameModel, breakdown: dict[AgentType, Counter[str]]
    ) -> None:
        if model.clock.tick == self._last_sample:
            return
        self._last_sample = model.clock.tick
        for kind, series in self._history.items():
            series.append(sum(breakdown.get(kind, Counter()).values()))

    def _draw_graph(self, surface: Surface, x: int, w: int, y: int) -> int:
        import pygame

        peak = max((max(s, default=0) for s in self._history.values()), default=0)

        scale = "log" if self.log_scale else "linear"
        cap = self._body_font.render(f"Population · {scale}", True, _MUTED)
        surface.blit(cap, (x, y))
        peak_surf = self._body_font.render(f"peak {peak}", True, _MUTED)
        surface.blit(peak_surf, (x + w - peak_surf.get_width(), y))
        y += cap.get_height() + 4

        h = 48
        pygame.draw.rect(surface, _GRAPH_BG, (x, y, w, h), border_radius=4)
        if peak > 0:
            for _, kind, color in _SECTIONS:
                series = self._history[kind]
                if len(series) < 2:
                    continue
                step = w / (len(series) - 1)
                points = [
                    (x + i * step, y + h - 3 - self._norm(v, peak) * (h - 6))
                    for i, v in enumerate(series)
                ]
                pygame.draw.lines(surface, color, False, points, 2)
        return y + h

    def _norm(self, value: int, peak: int) -> float:
        if self.log_scale:
            return math.log1p(value) / math.log1p(peak)
        return value / peak

    # --- Per-species card -----------------------------------------------------

    def _draw_card(
        self,
        surface: Surface,
        x: int,
        w: int,
        y: int,
        label: str,
        color: RGB,
        states: Counter[str],
    ) -> int:
        import pygame

        total = sum(states.values())
        ordered = sorted(states.items(), key=lambda kv: -kv[1])
        card_h = 26 + 12 + max(1, len(ordered)) * (self._body_font.get_height() + 1) + 8
        pygame.draw.rect(surface, _CARD_BG, (x, y, w, card_h), border_radius=6)
        pygame.draw.rect(surface, color, (x, y, 4, card_h),
                         border_top_left_radius=6, border_bottom_left_radius=6)

        ix = x + 14
        iw = w - 26
        cy = y + 7
        surface.blit(self._head_font.render(label, True, UI_FOREGROUND), (ix, cy))
        count = self._head_font.render(str(total), True, color)
        surface.blit(count, (x + w - 12 - count.get_width(), cy))
        cy += self._head_font.get_height() + 5

        cy = self._draw_segments(surface, ix, iw, cy, total, ordered) + 6
        for state, n in ordered:
            sc = _STATE_COLORS.get(state, _DEFAULT_STATE_COLOR)
            pygame.draw.rect(surface, sc, (ix, cy + 3, 9, 9), border_radius=2)
            surface.blit(self._body_font.render(state, True, _MUTED), (ix + 16, cy))
            num = self._body_font.render(str(n), True, UI_FOREGROUND)
            surface.blit(num, (x + w - 12 - num.get_width(), cy))
            cy += self._body_font.get_height() + 1
        return y + card_h

    def _draw_segments(
        self, surface: Surface, x: int, w: int, y: int, total: int, ordered: list
    ) -> int:
        import pygame

        bar_h = 10
        pygame.draw.rect(surface, _GRAPH_BG, (x, y, w, bar_h), border_radius=3)
        cursor = x
        for state, n in ordered:
            seg = round(w * n / total) if total else 0
            if seg <= 0:
                continue
            sc = _STATE_COLORS.get(state, _DEFAULT_STATE_COLOR)
            pygame.draw.rect(surface, sc, (cursor, y, seg, bar_h))
            cursor += seg
        return y + bar_h

    # --- Inspector ------------------------------------------------------------

    def _draw_inspector(
        self, surface: Surface, x: int, w: int, y: int, agent: BaseAgent, model: GameModel
    ) -> None:
        import pygame

        kind = getattr(agent, "agent_type", None)
        color = _COLOR_OF.get(kind, UI_FOREGROUND)
        pygame.draw.line(surface, (60, 64, 78), (x, y), (x + w, y))
        y += 8

        name = f"{kind.value.title() if kind else 'Agent'} #{agent.unique_id}"
        surface.blit(self._head_font.render(name, True, color), (x, y))
        y += self._head_font.get_height() + 4

        state = agent.brain.current.name if agent.brain and agent.brain.current else "—"
        surface.blit(self._body_font.render(f"state: {state}", True, _MUTED), (x, y))
        y += self._body_font.get_height() + 4

        hp = getattr(agent, "hp", None)
        if hp is not None:
            hp_max = _HP_MAX.get(kind, max(hp, 1.0))
            y = self._need_bar(surface, x, w, y, "hp", hp / hp_max, _HP_BAR)

        needs = getattr(agent, "needs", {})
        if Need.HUNGER in needs:
            y = self._need_bar(surface, x, w, y, "hunger", needs[Need.HUNGER], _HUNGER_BAR)
        if Need.ENERGY in needs:
            y = self._need_bar(surface, x, w, y, "energy", needs[Need.ENERGY], _ENERGY_BAR)

        inventory = getattr(agent, "inventory", None)
        if inventory is not None:
            wheat = inventory.quantity_of(ResourceType.WHEAT)
            gold = inventory.quantity_of(ResourceType.GOLD)
            line = f"wheat {wheat}   gold {gold}"
            surface.blit(self._body_font.render(line, True, UI_ACCENT), (x, y))
            y += self._body_font.get_height() + 2

        if agent.position is not None:
            pos = f"pos: ({agent.position[0]}, {agent.position[1]})"
            surface.blit(self._body_font.render(pos, True, _MUTED), (x, y))
            y += self._body_font.get_height() + 2

        self._draw_target(surface, x, y, agent, kind)

    def _draw_target(
        self, surface: Surface, x: int, y: int, agent: BaseAgent, kind: AgentType | None
    ) -> None:
        entry = _TARGETS.get(kind) if kind else None
        if entry is None:
            return
        label, other = entry
        found = nearest_of_type(agent, other)
        text = (
            f"{label}: ({found.position[0]}, {found.position[1]})"
            if found is not None and found.position is not None
            else f"{label}: none in sight"
        )
        surface.blit(self._body_font.render(text, True, _MUTED), (x, y))

    def _need_bar(
        self, surface: Surface, x: int, w: int, y: int, label: str, value: float, color: RGB
    ) -> int:
        import pygame

        tag = self._body_font.render(label, True, _MUTED)
        surface.blit(tag, (x, y))
        val = self._body_font.render(f"{value:.2f}", True, UI_FOREGROUND)
        surface.blit(val, (x + w - val.get_width(), y))
        by = y + tag.get_height() + 1
        bar_h = 7
        pygame.draw.rect(surface, _GRAPH_BG, (x, by, w, bar_h), border_radius=3)
        fill = round(w * max(0.0, min(1.0, value)))
        if fill > 0:
            pygame.draw.rect(surface, color, (x, by, fill, bar_h), border_radius=3)
        return by + bar_h + 6

    # --- Footer ---------------------------------------------------------------

    def _draw_footer(
        self,
        surface: Surface,
        x: int,
        w: int,
        bottom: int,
        paused: bool,
        sim_fps: int,
        model: GameModel,
        gold: int,
    ) -> None:
        y = bottom - 54
        if paused:
            status = self._body_font.render("PAUSED", True, (232, 170, 70))
        else:
            status = self._body_font.render(f"{sim_fps} steps/s", True, _MUTED)
        surface.blit(status, (x, y))
        economy = self._body_font.render(f"{gold}g · {model.trades} trades", True, UI_ACCENT)
        surface.blit(economy, (x + w - economy.get_width(), y))
        y += status.get_height() + 6
        for line in ("space pause · +/- speed · F food", "L scale · click to inspect"):
            surface.blit(self._small_font.render(line, True, (120, 126, 140)), (x, y))
            y += self._small_font.get_height() + 1

    # --- Extra dashboard rows -------------------------------------------------

    def _draw_alert(self, surface: Surface, x: int, w: int, y: int) -> int:
        import pygame

        h = self._body_font.get_height() + 6
        pygame.draw.rect(surface, (120, 40, 40), (x, y, w, h), border_radius=4)
        text = self._body_font.render("!  VILLAGE UNDER ATTACK", True, (250, 220, 210))
        surface.blit(text, (x + (w - text.get_width()) // 2, y + 3))
        return y + h

    def _draw_vitals(
        self, surface: Surface, model: GameModel, x: int, w: int, y: int
    ) -> int:
        died = sum(model.deaths.values())
        starved = model.deaths.get("starved", 0)
        left = self._body_font.render(f"+{model.births} born", True, (140, 190, 130))
        surface.blit(left, (x, y))
        right = self._body_font.render(
            f"-{died} died ({starved} starved)", True, (206, 130, 120)
        )
        surface.blit(right, (x + w - right.get_width(), y))
        return y + left.get_height()

    def _draw_roles(
        self, surface: Surface, x: int, w: int, y: int, roles: Counter[AgentType]
    ) -> int:
        parts = (
            f"folk {roles.get(AgentType.VILLAGER, 0)}",
            f"guard {roles.get(AgentType.GUARD, 0)}",
            f"farm {roles.get(AgentType.FARMER, 0)}",
            f"trade {roles.get(AgentType.MERCHANT, 0)}",
        )
        text = self._small_font.render("  ·  ".join(parts), True, (150, 156, 172))
        surface.blit(text, (x + 4, y))
        return y + text.get_height()

    # --- Data -----------------------------------------------------------------

    @staticmethod
    def _collect(
        model: GameModel,
    ) -> tuple[dict[AgentType, Counter[str]], Counter[AgentType], int]:
        """One pass over the agents: state breakdown, role counts, total gold."""
        breakdown: dict[AgentType, Counter[str]] = {}
        roles: Counter[AgentType] = Counter()
        gold = 0
        for agent in model.agents:
            kind = getattr(agent, "agent_type", None)
            if kind is None:
                continue
            roles[kind] += 1
            merged = _MERGE.get(kind, kind)
            brain = getattr(agent, "brain", None)
            state = brain.current.name if brain and brain.current else "-"
            breakdown.setdefault(merged, Counter())[state] += 1
            inventory = getattr(agent, "inventory", None)
            if inventory is not None:
                gold += inventory.quantity_of(ResourceType.GOLD)
        return breakdown, roles, gold

    def _ensure_fonts(self) -> None:
        if self._title_font is not None:
            return
        import pygame

        self._title_font = pygame.font.Font(None, 32)
        self._head_font = pygame.font.Font(None, 27)
        self._body_font = pygame.font.Font(None, 22)
        self._small_font = pygame.font.Font(None, 19)
