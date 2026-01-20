"""Tarot Oracle - AI-powered tarot divination system."""

from .tarot import (
    TarotDivination,
    SpreadRenderer,
    SPREADS,
    resolve_spread,
    Card,
    MAJOR_ARCANA,
    MINOR_ARCANA,
    SEMANTICS,
    DeckLoader,
    SemanticAdapter,
)
from .oracle import Oracle
from .config import Config
# Custom exceptions removed - using standard TypeError and ValueError instead

__version__ = "0.1.0"
__all__ = [
    "TarotDivination",
    "SpreadRenderer", 
    "SPREADS",
    "resolve_spread",
    "Card",
    "MAJOR_ARCANA",
    "MINOR_ARCANA",
    "SEMANTICS",
    "DeckLoader",
    "SemanticAdapter",
    "Oracle",
    "Config",
]
