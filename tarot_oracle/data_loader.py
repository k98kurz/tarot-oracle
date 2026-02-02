import json
from importlib import resources
from typing import Any


class BundledDataLoader:
    """Load bundled JSON data from the tarot_oracle package.

    Provides access to built-in decks and spreads installed via pip."""

    @staticmethod
    def load_deck(name: str) -> dict[str, Any] | None:
        """Load bundled deck configuration by name. Returns dict or None if not found."""
        resource_path = f"data/decks/{name}.json"
        try:
            with resources.files("tarot_oracle").joinpath(resource_path).open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    @staticmethod
    def load_spread(name: str) -> dict[str, Any] | None:
        """Load bundled spread configuration by name. Returns dict or None if not found."""
        resource_path = f"data/spreads/{name}.json"
        try:
            with resources.files("tarot_oracle").joinpath(resource_path).open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    @staticmethod
    def list_decks() -> list[str]:
        """List all bundled deck names. Returns list without .json extension."""
        return BundledDataLoader._list_files("data/decks")

    @staticmethod
    def list_spreads() -> list[str]:
        """List all bundled spread names. Returns list without .json extension."""
        return BundledDataLoader._list_files("data/spreads")

    @staticmethod
    def _list_files(dir_path: str) -> list[str]:
        """List JSON file stems in a package directory. Returns empty list if directory not found."""
        try:
            directory = resources.files("tarot_oracle").joinpath(dir_path)
            return [f.stem for f in directory.iterdir() if f.suffix == ".json"]
        except FileNotFoundError:
            return []

    @staticmethod
    def export_deck(name: str) -> str | None:
        """Export bundled deck as JSON string. Returns None if deck not found."""
        deck = BundledDataLoader.load_deck(name)
        if deck:
            return json.dumps(deck, indent=2)
        return None

    @staticmethod
    def export_spread(name: str) -> str | None:
        """Export bundled spread as JSON string. Returns None if spread not found."""
        spread = BundledDataLoader.load_spread(name)
        if spread:
            return json.dumps(spread, indent=2)
        return None
