#!/usr/bin/env python3

from secrets import token_bytes
from hashlib import sha256
from sys import argv, stdin
from argparse import ArgumentParser
from dataclasses import dataclass
from time import time
import ast
import json
import os
from pathlib import Path
from typing import Any, NoReturn, cast
from tarot_oracle.config import config
from tarot_oracle.loaders import SpreadLoader



# Comprehensive card keyword dictionaries (synthesized from Rider-Waite, Golden Dawn, Thoth traditions)
MAJOR_ARCANA = {
    "Fool": "New beginnings, innocence, spontaneity, trust, faith, leap of faith",
    "Magician": "Manifestation, skill, willpower, action, creation, resourcefulness, focused intention",
    "High Priestess": "Intuition, secrets, hidden knowledge, subconscious, mystery, divine feminine",
    "Empress": "Abundance, fertility, nurturing, nature, creativity, manifestation, earth mother",
    "Emperor": "Authority, structure, control, father figure, stability, leadership, establishment",
    "Hierophant": "Tradition, wisdom, institutions, conformity, spiritual guidance, organized belief",
    "Lovers": "Choice, partnership, harmony, union, alignment, values, soul connection",
    "Chariot": "Determination, victory, willpower, control, forward movement, self-discipline",
    "Strength": "Courage, inner strength, compassion, patience, taming wild nature, gentle power",
    "Hermit": "Introspection, soul searching, solitude, inner guidance, wisdom, spiritual isolation",
    "Wheel of Fortune": "Cycles, destiny, change, luck, turning points, karma, fate",
    "Justice": "Balance, fairness, truth, law, cause and effect, accountability, karmic justice",
    "Hanged Man": "Surrender, pause, new perspectives, sacrifice, letting go, suspension",
    "Death": "Transformation, endings, change, rebirth, transition, release, new chapter",
    "Temperance": "Moderation, balance, patience, synthesis, healing, middle path, alchemy",
    "Devil": "Bondage, materialism, addiction, shadow work, limitation, breaking chains",
    "Tower": "Upheaval, revelation, sudden change, chaos, awakening, truth revealed",
    "Star": "Hope, inspiration, guidance, healing, renewal, spiritual connection",
    "Moon": "Illusion, fear, anxiety, subconscious, intuition, hidden truths, dreams",
    "Sun": "Joy, success, vitality, clarity, optimism, achievement, enlightenment",
    "Judgement": "Awakening, rebirth, calling, purpose, forgiveness, new phase",
    "World": "Completion, integration, accomplishment, fulfillment, wholeness, success"
}

MINOR_ARCANA = {
    # Wands (Fire energy)
    "W_A": "Fire energy, new beginnings, creative spark, inspiration, passion, initiative, opportunity",
    "W_2": "Fire energy, planning, future vision, making decisions, progress, forward movement",
    "W_3": "Fire energy, expansion, growth, celebration, communication, leadership, future planning",
    "W_4": "Fire energy, stability, foundation, security, celebration, harmony, homecoming",
    "W_5": "Fire energy, competition, conflict, inner strength, challenge, sportsmanship",
    "W_6": "Fire energy, victory, recognition, public success, achievement, acclaim",
    "W_7": "Fire energy, defense, courage, conviction, standing ground, moral position",
    "W_8": "Fire energy, rapid movement, messages, communication, quick action, haste",
    "W_9": "Fire energy, strength, resilience, protection, readiness, defense",
    "W_10": "Fire energy, completion, fulfillment, responsibility, burden, success",
    "W_P": "Fire energy, creative spark, new passion, youthful enthusiasm, opportunity",
    "W_N": "Fire energy, action, movement, swift change, enthusiasm, adventure",
    "W_Q": "Fire energy, mature creativity, leadership, confidence, passion, inspiration",
    "W_K": "Fire energy, mastery, creative leadership, vision, inspiration, authority",

    # Cups (Water energy)
    "C_A": "Water energy, emotional new beginnings, love, intuition, new relationships, creative flow",
    "C_2": "Water energy, partnership, harmony, union, emotional connection, balance",
    "C_3": "Water energy, celebration, community, friendship, emotional abundance, joy",
    "C_4": "Water energy, emotional security, stability, foundations, home, relationships",
    "C_5": "Water energy, loss, disappointment, emotional transition, letting go, change",
    "C_6": "Water energy, emotional support, generosity, sharing, giving, nostalgia",
    "C_7": "Water energy, choices, reflection, inner wisdom, emotional decision, retreat",
    "C_8": "Water energy, moving on from emotional past, new opportunities, change, transition",
    "C_9": "Water energy, emotional satisfaction, dreams fulfilled, wishes come true, contentment",
    "C_10": "Water energy, emotional completion, family harmony, emotional abundance, fulfillment",
    "C_P": "Water energy, emotional curiosity, creative intuition, new emotional opportunities",
    "C_N": "Water energy, emotional action, romance, communication, messages, movement",
    "C_Q": "Water energy, emotional mastery, compassion, nurturing, mature feelings, wisdom",
    "C_K": "Water energy, emotional control, stability, mature emotions, relationship mastery",

    # Swords (Air energy)
    "S_A": "Air energy, mental clarity, new ideas, breakthrough, intellectual power, truth",
    "S_2": "Air energy, indecision, stalemate, choices, mental conflict, blocked thinking",
    "S_3": "Air energy, heartbreak, sorrow, painful truth, mental separation, grief",
    "S_4": "Air energy, rest, meditation, recovery, mental pause, truce",
    "S_5": "Air energy, victory through cunning, strategy, escape, Pyrrhic victory",
    "S_6": "Air energy, mental recovery, new paths, moving on, intellectual transition",
    "S_7": "Air energy, deception, strategy, withdrawal, cunning, intellect, escape",
    "S_8": "Air energy, mental restriction, feeling trapped, isolation, powerlessness",
    "S_9": "Air energy, mental anguish, worry, anxiety, sleepless nights, mental burden",
    "S_10": "Air energy, mental ruin, complete breakdown, disaster, bottom, rock bottom",
    "S_P": "Air energy, mental curiosity, new ideas, intellectual opportunity, learning",
    "S_N": "Air energy, intellectual action, communication, messages, change, movement",
    "S_Q": "Air energy, intellectual mastery, wisdom, emotional clarity, mature thinking",
    "S_K": "Air energy, mental power, authority, intellectual control, truth, command",

    # Pentacles (Earth energy)
    "P_A": "Earth energy, material new beginnings, prosperity, opportunity, manifestation",
    "P_2": "Earth energy, financial balance, juggling resources, flexibility, adaptation",
    "P_3": "Earth energy, skilled work, craftsmanship, collaboration, team effort, mastery",
    "P_4": "Earth energy, material security, stability, foundations, conservation, protection",
    "P_5": "Earth energy, material hardship, poverty, isolation, spiritual seeking",
    "P_6": "Earth energy, material generosity, giving, sharing, wealth distribution, charity",
    "P_7": "Earth energy, material patience, waiting, investment, long-term planning, harvest",
    "P_8": "Earth energy, skill mastery, apprenticeship, detailed work, craftsmanship",
    "P_9": "Earth energy, material abundance, luxury, success, financial security, comfort",
    "P_10": "Earth energy, material completion, family wealth, inheritance, legacy, fulfillment",
    "P_P": "Earth energy, material opportunity, learning, study, practical skills, manifestation",
    "P_N": "Earth energy, material action, steady progress, reliable work, methodical approach",
    "P_Q": "Earth energy, material nurturing, practical wisdom, abundance, prosperity management",
    "P_K": "Earth energy, material mastery, worldly success, enterprise, stability, wealth"
}


# Pre-defined spreads
SPREADS = {
    '3-card': [[2, 1, 3]],
    'cross': [
        [0, 5, 0],
        [2, 1, 3],
        [0, 4, 0]
    ],
    'celtic': [
        [0, 5, 0, 0, 7],
        [4, 1, 6, 0, 8],
        [0, 2, 0, 0, 9],
        [0, 3, 0, 0, 10]
    ],
    'single': [[1]],
    'crowley': [
        [13,  9,  5,  0,  4,  8, 12],
        [ 0,  0,  2,  1,  3,  0,  0],
        [14, 10,  6,  0,  7, 11, 15]
    ],
}

_earth = 'Potential Future/Natural Path (Earth)'
_water = 'Far/Alternate Future Path (Water)'
_air = 'Psychic Basis/Mutable Influences (Air)'
_fire = 'Karmic Forces/Cosmic Influences (Fire)'
_spirit = 'Nature of Circumstances (Spirit)'

# Variable definitions for semantic placeholders
VARIABLE_DEFINITIONS = {
    'water': 'Emotional Basis/Subconscious Influences (Water)',
    'fire': 'Karmic Forces/Cosmic Influences (Fire)', 
    'air': 'Psychic Basis/Mutable Influences (Air)',
    'earth': 'Material/Foundation/Practical Influences (Earth)',
    'spirit': 'Nature of Circumstances/Divine Will (Spirit)'
}

SEMANTICS = {
    '3-card': [['Past/Querent/Situation/Idea', 'Present/Path/Action/Process', 'Future/Potential/Outcome/Aspiration']],
    'cross': [
        ['', 'Potential', ''],
        ['Past', 'Present', 'Future'],
        ['', 'Core Reason', '']],
    'celtic': [
        ['', 'Goal/Potential/Best Outcome', '', '', 'Previous Experiences/Attitudes'],
        ['Recent Past', 'Present/Theme/Querent\'s Role', 'Near Future', '', "External Influences (Environment/Social)"],
        ['', 'Primary Obstable/Challenge', '', '', 'Hopes/Fears'],
        ['', 'Pyschic/Subconscious Foundations of the Issue', '', '', 'Probable/Natural Outcome']
    ],
    'single': [['Contemplation on Question/Potential Answer/Guidance']],
    'crowley': [
        [_water,  _water,  _water,  '',  _earth,  _earth, _earth],
        [ '',  '',  _spirit,  'Querent/Present (Spirit)',  _spirit,  '',  ''],
        [_air, _air,  _air,  '',  _fire, _fire, _fire]
    ],
}


class SemanticAnalyzer:
    """Analyzes semantic patterns and provides rule-based interpretation guidance."""
    
    def __init__(self, semantic_config: dict[str, Any] | None = None) -> None:
        """Initialize analyzer with semantic configuration.
        
        Args:
            semantic_config: Dictionary containing semantic_groups, semantics, and guidance rules
        """
        self.semantic_groups = semantic_config.get('semantic_groups', {}) if semantic_config else {}
        self.semantics_matrix = semantic_config.get('semantics', []) if semantic_config else []
        self.guidance_rules = semantic_config.get('guidance_rules', []) if semantic_config else []
    
    def resolve_variables(self, text: str) -> str:
        """Replace variable placeholders with their definitions.
        
        Args:
            text: Text containing variable placeholders like ${water}
            
        Returns:
            Text with placeholders replaced by their definitions
        """
        import re
        
        for var_name, definition in VARIABLE_DEFINITIONS.items():
            placeholder = f"${{{var_name}}}"
            text = text.replace(placeholder, definition)
        
        return text
    
    def analyze_card_combinations(self, cards: list['Card']) -> dict[str, Any]:
        """Analyze combinations of cards for patterns.
        
        Args:
            cards: List of cards drawn in the reading
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            'elemental_balance': self._analyze_elemental_balance(cards),
            'major_arcana_count': sum(1 for card in cards if card.card_type == 'major'),
            'minor_arcana_count': sum(1 for card in cards if card.card_type == 'minor'),
            'court_cards_count': sum(1 for card in cards if card.card_type == 'minor' and self._is_court_card(card)),
            'reversed_count': sum(1 for card in cards if hasattr(card, 'is_reversed') and card.is_reversed),
            'suit_distribution': self._analyze_suit_distribution(cards),
            'numeral_distribution': self._analyze_numeral_distribution(cards),
            'card_count': len(cards)
        }
        
        return analysis
    
    def _analyze_elemental_balance(self, cards: list['Card']) -> dict[str, int]:
        """Analyze elemental balance in the reading."""
        elements = {'fire': 0, 'water': 0, 'air': 0, 'earth': 0}
        
        for card in cards:
            if card.card_type == 'minor':
                if card.suit == 'W':  # Wands
                    elements['fire'] += 1
                elif card.suit == 'C':  # Cups
                    elements['water'] += 1
                elif card.suit == 'S':  # Swords
                    elements['air'] += 1
                elif card.suit == 'P':  # Pentacles
                    elements['earth'] += 1
        
        return elements
    
    def _analyze_suit_distribution(self, cards: list['Card']) -> dict[str, int]:
        """Analyze distribution of suits in minor arcana cards."""
        suits = {'Wands': 0, 'Cups': 0, 'Swords': 0, 'Pentacles': 0}
        
        for card in cards:
            if card.card_type == 'minor':
                suit_names = {'W': 'Wands', 'C': 'Cups', 'S': 'Swords', 'P': 'Pentacles'}
                if card.suit in suit_names:
                    suits[suit_names[card.suit]] += 1
        
        return suits
    
    def _is_court_card(self, card: 'Card') -> bool:
        """Check if a card is a court card."""
        if card.card_type != 'minor':
            return False
        
        court_values = {'Page', 'Knight', 'Queen', 'King'}
        return card.value in court_values
    
    def _analyze_numeral_distribution(self, cards: list['Card']) -> dict[str, int]:
        """Analyze distribution of numerals in minor arcana cards."""
        numerals = {'Aces': 0, 'Number cards': 0, 'Court cards': 0}
        
        for card in cards:
            if card.card_type == 'minor':
                if self._is_court_card(card):
                    numerals['Court cards'] += 1
                elif card.value == 'A':
                    numerals['Aces'] += 1
                else:
                    numerals['Number cards'] += 1
        
        return numerals
    
    def generate_guidance(self, cards: list['Card'], semantic_groups: dict[str, list['Card']]) -> list[str]:
        """Generate guidance based on rules and card analysis.
        
        Args:
            cards: List of cards drawn
            semantic_groups: Cards grouped by semantic meaning
            
        Returns:
            List of guidance strings in markdown format
        """
        guidance = []
        analysis = self.analyze_card_combinations(cards)
        
        # Apply guidance rules
        for rule in self.guidance_rules:
            if self._rule_matches(rule, cards, analysis, semantic_groups):
                guidance_text = self.resolve_variables(rule.get('guidance', ''))
                if guidance_text:
                    guidance.append(f"- {guidance_text}")
        
        # Add general insights based on analysis
        if analysis['major_arcana_count'] > len(cards) // 2:
            guidance.append("- **Major Arcana Dominance**: This reading carries significant spiritual or karmic weight")
        
        if analysis['reversed_count'] > len(cards) // 2:
            guidance.append("- **Many Reversed Cards**: Expect challenges, delays, or internal blockages")
        
        return guidance
    
    def _rule_matches(self, rule: dict[str, Any], cards: list['Card'], analysis: dict[str, Any], semantic_groups: dict[str, list['Card']]) -> bool:
        """Check if a guidance rule matches the current reading."""
        conditions = rule.get('conditions', {})
        
        # Check card conditions
        if 'cards' in conditions:
            for card_condition in conditions['cards']:
                if not self._card_condition_matches(card_condition, cards, semantic_groups):
                    return False
        
        # Check analysis conditions  
        if 'major_arcana_min' in conditions:
            if analysis['major_arcana_count'] < conditions['major_arcana_min']:
                return False
        
        if 'major_arcana_max' in conditions:
            if analysis['major_arcana_count'] > conditions['major_arcana_max']:
                return False
        
        if 'minor_arcana_min' in conditions:
            if analysis['minor_arcana_count'] < conditions['minor_arcana_min']:
                return False
        
        if 'court_cards_min' in conditions:
            if analysis['court_cards_count'] < conditions['court_cards_min']:
                return False
        
        if 'reversed_min' in conditions:
            if analysis['reversed_count'] < conditions['reversed_min']:
                return False
        
        if 'reversed_max' in conditions:
            if analysis['reversed_count'] > conditions['reversed_max']:
                return False
        
        # Check elemental conditions
        if 'elemental_balance' in conditions:
            element_conditions = conditions['elemental_balance']
            for element, min_count in element_conditions.items():
                if analysis['elemental_balance'].get(element, 0) < min_count:
                    return False
        
        return True
    
    def _card_condition_matches(self, card_condition: dict[str, Any], cards: list['Card'], semantic_groups: dict[str, list['Card']]) -> bool:
        """Check if a specific card condition matches."""
        condition_type = card_condition.get('type')
        
        if condition_type == 'in_group':
            group_name = card_condition.get('group')
            if group_name in semantic_groups:
                group_cards = semantic_groups[group_name]
                required_cards = card_condition.get('cards', [])
                for req_card in required_cards:
                    if not any(card.name == req_card or card.get_notation() == req_card for card in group_cards):
                        return False
                return True
        
        elif condition_type == 'anywhere':
            required_cards = card_condition.get('cards', [])
            card_names = [card.name for card in cards] + [card.get_notation() for card in cards]
            for req_card in required_cards:
                if req_card in card_names:
                    return True
            return False
        
        elif condition_type == 'suit_present':
            required_suits = card_condition.get('suits', [])
            card_suits = [card.suit for card in cards if card.card_type == 'minor' and card.suit]
            for suit in required_suits:
                if suit in card_suits:
                    return True
            return False
        
        elif condition_type == 'card_type_count':
            card_type = card_condition.get('card_type')  # 'major' or 'minor'
            min_count = card_condition.get('min_count', 1)
            max_count = card_condition.get('max_count', len(cards))
            
            type_count = sum(1 for card in cards if card.card_type == card_type)
            return min_count <= type_count <= max_count
        
        elif condition_type == 'not_present':
            excluded_cards = card_condition.get('cards', [])
            card_names = [card.name for card in cards] + [card.get_notation() for card in cards]
            for excluded_card in excluded_cards:
                if excluded_card in card_names:
                    return False
            return True
        
        return False


class DeckLoader:
    """Handles loading and management of tarot deck configurations."""

    def resolve_deck_path(self, filename: str) -> str | None:
        """Resolve deck filename using search order with security validation:
        1. ./{filename}
        2. ./{filename}.json
        3. ~/.tarot-oracle/decks/{filename}
        4. ~/.tarot-oracle/decks/{filename}.json
        """
        from tarot_oracle.config import config
        
        # Sanitize filename to prevent path traversal
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        safe_filename = safe_filename.lstrip('.-')
        if not safe_filename:
            return None
            
        search_paths = [
            Path.cwd() / safe_filename,
            Path.cwd() / f"{safe_filename}.json",
            config.decks_dir / safe_filename,
            config.decks_dir / f"{safe_filename}.json"
        ]

        for path in search_paths:
            if path.exists() and path.is_file():
                resolved = path.resolve()
                # Ensure path is within expected directories
                if (resolved.is_relative_to(Path.cwd()) or 
                    resolved.is_relative_to(config.home_dir)):
                    return str(resolved)
        return None

    @staticmethod
    def load_deck_config(path: str) -> dict:
        """Load and validate JSON deck configuration."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Basic validation
            if not isinstance(config, dict):
                raise ValueError("Deck configuration must be a JSON object")

            # Validate required top-level fields
            if 'name' not in config:
                raise ValueError("Deck configuration must include 'name' field")

            return config

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in deck file: {e}")
        except FileNotFoundError:
            raise ValueError(f"Deck file not found: {path}")
        except Exception as e:
            raise ValueError(f"Error loading deck file: {e}")

    def list_available_decks(self) -> list[dict[str, str]]:
        """Scan ~/.tarot-oracle/decks/ and return deck metadata."""
        from tarot_oracle.config import config
        decks_dir = config.decks_dir

        if not decks_dir.exists() or not decks_dir.is_dir():
            return []

        decks = []

        # Find all .json files in the decks directory
        for json_file in decks_dir.glob("*.json"):
            try:
                config = DeckLoader.load_deck_config(str(json_file))
                decks.append({
                    "filename": json_file.name,
                    "name": config.get("name", "Unnamed Deck"),
                    "description": config.get("description", "No description available")
                })
            except Exception:
                # Skip invalid deck files
                continue

        # Sort by filename for consistent ordering
        decks.sort(key=lambda x: x["filename"])
        return decks


@dataclass
class Card:
    """Represents a single tarot card."""
    name: str
    card_type: str  # 'major' or 'minor'
    suit: str|None  # W, C, S, P or None for major arcana
    value: str  # Roman numeral for major, numeric/letter for minor
    keywords: str  # Card interpretation keywords
    reversed_keywords: str|None = None  # Optional reversed card meanings
    is_reversed: bool = False  # Set during shuffling

    def get_keywords(self) -> str:
        """Get appropriate keywords based on reversal state."""
        if self.is_reversed and self.reversed_keywords:
            return self.reversed_keywords
        return self.keywords

    def get_notation_code(self) -> str:
        """Get raw card notation without formatting."""
        if self.card_type == 'major':
            return self.value  # Roman numeral or 0 for Fool
        else:
            return f"{self.suit}{self.value}"  # e.g., W3, CK, PN

    def get_notation(self) -> str:
        """Get card notation with reversal formatting (7 characters wide)."""
        code = self.get_notation_code()
        if self.is_reversed:
            # [↓XVI] = 7 chars: [ + ↓ + 4 chars + ]
            return f"[↓{code:<4}]"
        else:
            # [ XVI ] = 7 chars: [ + space + 4 chars + ]
            return f"[ {code:<4}]"


class DeterministicRNG:
    """Simple linear congruential generator for deterministic random numbers."""

    def __init__(self, seed: int) -> None:
        self.state = seed

    def next_int(self, max_value: int) -> int:
        """Generate next pseudo-random integer."""
        self.state = (self.state * 1103515245 + 12345) & 0x7fffffff
        return self.state % max_value


class Deck:
    """Tarot deck with card loading and shuffling functionality."""

    def __init__(self, deck_path: str | None = None) -> None:
        self.cards = []
        self.shuffled = []

        if deck_path:
            self.cards = self._load_custom_deck(deck_path)
        else:
            self.cards = self._create_deck()

    def _load_custom_deck(self, deck_path: str) -> list[Card]:
        """Load deck from JSON configuration file."""
        config = DeckLoader.load_deck_config(deck_path)
        cards = []

        # Load Major Arcana
        if 'major_arcana' in config:
            for card_data in config['major_arcana']:
                name = card_data.get('name', 'Unknown')
                value = card_data.get('value', '0')
                keywords = card_data.get('keywords', '')
                reversed_keywords = card_data.get('reversed')

                card = Card(
                    name=name,
                    card_type='major',
                    suit=None,
                    value=value,
                    keywords=keywords,
                    reversed_keywords=reversed_keywords
                )
                cards.append(card)

        # Load Minor Arcana
        if 'minor_arcana' in config:
            for card_data in config['minor_arcana']:
                suit = card_data.get('suit')
                suit_name = card_data.get('suit_name', 'Unknown')
                value = card_data.get('value', '0')
                name = card_data.get('name', f"{value} of {suit_name}")
                keywords = card_data.get('keywords', '')
                reversed_keywords = card_data.get('reversed')

                if not suit or not value:
                    continue  # Skip invalid cards

                card = Card(
                    name=name,
                    card_type='minor',
                    suit=suit,
                    value=value,
                    keywords=keywords,
                    reversed_keywords=reversed_keywords
                )
                cards.append(card)

        if not cards:
            raise ValueError("No valid cards found in deck configuration")

        return cards

    def _create_deck(self) -> list[Card]:
        """Create the standard 78-card tarot deck."""
        cards = []

        # Major Arcana (0-21)
        major_arcana = [
            ("Fool", "0"), ("Magician", "I"), ("High Priestess", "II"), ("Empress", "III"),
            ("Emperor", "IV"), ("Hierophant", "V"), ("Lovers", "VI"), ("Chariot", "VII"),
            ("Strength", "VIII"), ("Hermit", "IX"), ("Wheel of Fortune", "X"), ("Justice", "XI"),
            ("Hanged Man", "XII"), ("Death", "XIII"), ("Temperance", "XIV"), ("Devil", "XV"),
            ("Tower", "XVI"), ("Star", "XVII"), ("Moon", "XVIII"), ("Sun", "XIX"),
            ("Judgement", "XX"), ("World", "XXI")
        ]

        for name, value in major_arcana:
            keywords = MAJOR_ARCANA[name]
            cards.append(Card(name, 'major', None, value, keywords))

        # Minor Arcana - 4 suits, 14 cards each
        suits = {'W': 'Wands', 'C': 'Cups', 'S': 'Swords', 'P': 'Pentacles'}
        values = [
            ('A', 'Ace'), ('2', 'Two'), ('3', 'Three'), ('4', 'Four'), ('5', 'Five'),
            ('6', 'Six'), ('7', 'Seven'), ('8', 'Eight'), ('9', 'Nine'), ('10', 'Ten'),
            ('P', 'Page'), ('N', 'Knight'), ('Q', 'Queen'), ('K', 'King')
        ]

        for suit_letter, suit_name in suits.items():
            for value_letter, value_name in values:
                card_name = f"{value_name} of {suit_name}"
                desc_key = f"{suit_letter}_{value_letter}"
                keywords = MINOR_ARCANA[desc_key]
                cards.append(Card(card_name, 'minor', suit_letter, value_letter, keywords))

        return cards

    def shuffle_and_assign_reversals(self, rng: DeterministicRNG, allow_reversed: bool = False) -> None:
        """Shuffle the deck using Fisher-Yates algorithm and assign reversals."""
        self.shuffled = self.cards.copy()
        n = len(self.shuffled)

        # Fisher-Yates shuffle
        for i in range(n - 1, 0, -1):
            j = rng.next_int(i + 1)
            self.shuffled[i], self.shuffled[j] = self.shuffled[j], self.shuffled[i]

        # Assign reversals during shuffle
        if allow_reversed:
            for card in self.shuffled:
                card.is_reversed = (rng.next_int(2) == 1)  # 50% chance

    def shuffle(self, rng: DeterministicRNG) -> None:
        """Shuffle the deck using Fisher-Yates algorithm."""
        self.shuffle_and_assign_reversals(rng, allow_reversed=False)

    def draw_cards(self, count: int) -> list[Card]:
        """Draw specified number of cards from shuffled deck."""
        if not self.shuffled:
            raise ValueError("Deck must be shuffled before drawing cards")
        return self.shuffled[:count]


class SpreadRenderer:
    """Renders tarot spreads in terminal ASCII format."""

    @staticmethod
    def format_card_simple(card: Card) -> str:
        """Format a card as simple bracket notation with 8-char width."""
        return f"{card.get_notation()}"  # Use enhanced notation with reversal support

    @staticmethod
    def render_spread(cards: list[Card], spread_layout: list[list[int]]) -> str:
        """Render the complete spread with simple notation."""
        # Check if this is a matrix layout (more than one row)
        is_matrix = len(spread_layout) > 1
        
        if is_matrix:
            # Handle as matrix
            flat_positions = []
            for row in spread_layout:
                for pos in row:
                    flat_positions.append(pos)

            unique_positions = sorted(set(pos for pos in flat_positions if pos > 0))
            position_to_card = {}
            for i, position in enumerate(unique_positions):
                if i < len(cards):
                    position_to_card[position] = cards[i]

            rows = []
            for row in spread_layout:
                row_strings = []
                for position in row:
                    if position == 0:
                        row_strings.append(" " * 7)  # 7 spaces for empty position
                    else:
                        row_strings.append(SpreadRenderer.format_card_simple(position_to_card[position]))
                rows.append((" " * 3).join(row_strings))  # 3 spaces between cards
            return "\n\n".join(rows)  # Single blank line between rows
        else:
            # Handle as linear - extract the single row
            linear_layout = spread_layout[0] if spread_layout else []
            unique_positions = sorted(set(pos for pos in linear_layout if pos > 0))
            position_to_card = {}
            for i, position in enumerate(unique_positions):
                if i < len(cards):
                    position_to_card[position] = cards[i]

            card_strings = []
            for position in linear_layout:
                if position == 0:
                    card_strings.append("        ")  # 8 spaces for empty position
                else:
                    card_strings.append(SpreadRenderer.format_card_simple(position_to_card[position]))

            return " ".join(card_strings)  # Single space between cards

    @staticmethod
    def render_legend(cards: list[Card], include_keywords: bool = False) -> str:
        """Render the legend for drawn cards in drawing order."""
        if not cards:
            return ""

        legend_lines = ["Legend:"]
        for card in cards:
            if card.card_type == 'major':
                type_name = "Major Arcana"
            else:
                suit_names = {'W': 'Wands', 'C': 'Cups', 'S': 'Swords', 'P': 'Pentacles'}
                type_name = suit_names[card.suit or '']

            legend_line = f"{card.get_notation()} - {card.name} ({type_name})"
            if include_keywords:
                legend_line += f": {card.get_keywords()}"
            legend_lines.append(legend_line)

        return "\n".join(legend_lines)

    @staticmethod
    def render_spread_json(cards: list[Card], spread_layout: list[list[int]]) -> list[list[str]]:
        """Render spread as JSON matrix mirroring ASCII format."""
        # Check if this is a matrix layout (more than one row)
        is_matrix = len(spread_layout) > 1

        if is_matrix:
            # Handle as matrix - return 2D array
            flat_positions = []
            for row in spread_layout:
                for pos in row:
                    flat_positions.append(pos)

            unique_positions = sorted(set(pos for pos in flat_positions if pos > 0))
            position_to_card = {}
            for i, position in enumerate(unique_positions):
                if i < len(cards):
                    position_to_card[position] = cards[i]

            rows = []
            for row in spread_layout:
                row_strings = []
                for position in row:
                    if position == 0:
                        row_strings.append("    ")  # 4 spaces for empty position
                    else:
                        row_strings.append(position_to_card[position].get_notation())
                rows.append(row_strings)
            return rows
        else:
            # Handle as linear - return single row array
            linear_layout = spread_layout[0] if spread_layout else []
            unique_positions = sorted(set(pos for pos in linear_layout if pos > 0))
            position_to_card = {}
            for i, position in enumerate(unique_positions):
                if i < len(cards):
                    position_to_card[position] = cards[i]

            card_strings = []
            for position in linear_layout:
                if position == 0:
                    card_strings.append("    ")  # 7 spaces for empty position
                else:
                    card_strings.append(position_to_card[position].get_notation())

            return [card_strings]  # Return as single row for consistency

    @staticmethod
    def render_legend_json(cards: list[Card], include_keywords: bool = True) -> list[dict[str, Any]]:
        """Render legend as structured list of card dictionaries."""
        if not cards:
            return []

        legend_data = []
        for card in cards:
            if card.card_type == 'major':
                type_name = "Major Arcana"
            else:
                suit_names = {'W': 'Wands', 'C': 'Cups', 'S': 'Swords', 'P': 'Pentacles'}
                type_name = suit_names[card.suit or '']

            card_dict = {
                "notation": card.get_notation(),
                "name": card.name,
                "type": type_name
            }

            if include_keywords:
                card_dict["keywords"] = card.get_keywords()

            legend_data.append(card_dict)

        return legend_data

    @staticmethod
    def render_json(cards: list[Card], spread_layout: list[list[int]], include_legend: bool = True) -> dict[str, Any]:
        """Render complete reading as JSON structure."""
        matrix = SpreadRenderer.render_spread_json(cards, spread_layout)
        result: dict[str, Any] = {"spread": matrix}

        if include_legend:
            result["legend"] = SpreadRenderer.render_legend_json(cards, include_keywords=True)

        return result

    @staticmethod
    def render_semantic_legend(cards: list[Card], layout: list[list[int]],
                           semantics: list[list[str]]|None = None,
                           include_keywords: bool = False) -> str:
        """Render legend with semantic groupings."""
        adapter = SemanticAdapter(layout, cards, semantics)
        return adapter.render_semantic_legend(include_keywords)

    @staticmethod
    def render_descriptions(cards: list[Card]) -> str:
        """Render card descriptions for drawn cards."""
        if not cards:
            return ""

        description_lines = ["Card Keywords:"]
        for card in cards:
            description_lines.append(f"{card.get_notation()} {card.get_keywords()}")

        return "\n".join(description_lines)


class SemanticAdapter:
    """Maps cards to semantic meanings based on spread position."""

    def __init__(self, layout: list[list[int]], cards: list[Card], semantics: list[list[str]]|None = None, 
                 semantic_config: dict[str, Any]|None = None) -> None:
        """Enhanced SemanticAdapter with support for custom configurations.
        
        Args:
            layout: Card position layout matrix
            cards: List of drawn cards
            semantics: Optional semantics matrix (for backward compatibility)
            semantic_config: Custom semantic configuration with groups and guidance
        """
        self.layout = layout
        self.cards = cards
        self.semantics = semantics or []
        self.semantic_config = semantic_config or {}
        self.analyzer = SemanticAnalyzer(semantic_config) if semantic_config else None
        
        # Process custom semantics from config if available
        if not self.semantics and 'semantics' in self.semantic_config:
            # Resolve variable placeholders in semantics
            resolved_semantics = []
            for row in self.semantic_config['semantics']:
                resolved_row = []
                for cell in row:
                    if isinstance(cell, str):
                        resolved_cell = self.analyzer.resolve_variables(cell) if self.analyzer else cell
                        resolved_row.append(resolved_cell)
                    else:
                        resolved_row.append(cell)
                resolved_semantics.append(resolved_row)
            self.semantics = resolved_semantics
        
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """Validate layout and semantics have compatible dimensions."""
        if not self.semantics:
            return  # Empty semantics always valid

        if len(self.layout) != len(self.semantics):
            raise ValueError('dimensions of layout and semantics are incompatible')

        for layout_row, semantic_row in zip(self.layout, self.semantics):
            if len(layout_row) != len(semantic_row):
                raise ValueError('dimensions of layout and semantics are incompatible')

    def _get_semantic_for_position(self, position: int) -> str|None:
        """Find semantic value for a given position in layout."""
        if not self.semantics:
            return None

        for row_idx, layout_row in enumerate(self.layout):
            for col_idx, pos in enumerate(layout_row):
                if pos == position:
                    semantic = self.semantics[row_idx][col_idx]
                    return semantic if semantic else None
        return None

    def _build_card_index_to_semantic(self) -> dict[int, str]:
        """Map card drawing order to semantic meanings."""
        # Extract and sort unique positions (same as render_spread_json)
        flat_positions = []
        for row in self.layout:
            for pos in row:
                flat_positions.append(pos)

        unique_positions = sorted(set(pos for pos in flat_positions if pos > 0))

        card_index_to_semantic = {}
        for card_idx, position in enumerate(unique_positions):
            semantic = self._get_semantic_for_position(position)
            if semantic:
                card_index_to_semantic[card_idx] = semantic
            # No semantic = falls under "General Information"

        return card_index_to_semantic

    def _group_cards_by_semantic(self) -> dict[str, list[Card]]:
        """Group cards by semantic meanings."""
        card_index_to_semantic = self._build_card_index_to_semantic()
        semantic_to_cards = {}

        for card_idx, card in enumerate(self.cards):
            semantic = card_index_to_semantic.get(card_idx, "General Information")
            if semantic not in semantic_to_cards:
                semantic_to_cards[semantic] = []
            semantic_to_cards[semantic].append(card)

        return semantic_to_cards

    def _format_card_line(self, card: Card, include_keywords: bool) -> str:
        """Format individual card line for legend."""
        if card.card_type == 'major':
            type_name = "Major Arcana"
        else:
            suit_names = {'W': 'Wands', 'C': 'Cups', 'S': 'Swords', 'P': 'Pentacles'}
            type_name = suit_names[card.suit or '']

        # Reversed indicator already in notation via [↓] prefix
        legend_line = f"  {card.get_notation()} - {card.name} ({type_name})"
        if include_keywords:
            legend_line += f": {card.get_keywords()}"

        return legend_line

    def render_semantic_legend(self, include_keywords: bool = False) -> str:
        """Render legend with semantic groupings."""
        semantic_groups = self._group_cards_by_semantic()

        if not self.cards:
            return ""

        lines = []

        # Process semantic groups (alphabetical order for simplicity)
        semantic_keys = [k for k in semantic_groups.keys() if k != "General Information"]
        semantic_keys.sort()

        # Add first semantic group without leading newline
        if semantic_keys:
            lines.append(f"{semantic_keys[0]}:")
            for card in semantic_groups[semantic_keys[0]]:
                lines.append(self._format_card_line(card, include_keywords))

        # Add remaining semantic groups with leading newlines
        for semantic in semantic_keys[1:]:
            lines.append(f"\n{semantic}:")
            for card in semantic_groups[semantic]:
                lines.append(self._format_card_line(card, include_keywords))

        # Add General Information last if it exists
        if "General Information" in semantic_groups:
            # Add leading newline if there were semantic groups, otherwise it's first
            if lines:
                lines.append(f"\nGeneral Information:")
            else:
                lines.append(f"General Information:")
            for card in semantic_groups["General Information"]:
                lines.append(self._format_card_line(card, include_keywords))

        return "\n".join(lines)

    
    def get_semantic_groups(self) -> dict[str, list[Card]]:
        """Get semantic groups with support for custom semantic_groups from config."""
        # First, try to get custom semantic groups from config
        if self.analyzer and 'semantic_groups' in self.semantic_config:
            custom_groups = self.semantic_config['semantic_groups']
            result_groups = {}
            
            # Process custom semantic groups
            for group_name, group_info in custom_groups.items():
                if isinstance(group_info, dict) and 'positions' in group_info:
                    # Group defined by positions
                    group_cards = []
                    for pos in group_info['positions']:
                        card = self._get_card_at_position(pos)
                        if card:
                            group_cards.append(card)
                    
                    if group_cards:
                        description = group_info.get('description', group_name)
                        result_groups[description] = group_cards
            
            # Merge with traditional semantic grouping
            traditional_groups = self._group_cards_by_semantic()
            result_groups.update(traditional_groups)
            return result_groups
        
        # Fall back to traditional semantic grouping
        return self._group_cards_by_semantic()
    
    def _get_card_at_position(self, position: int) -> Card | None:
        """Get card at specific position in layout."""
        # Extract and sort unique positions
        flat_positions = []
        for row in self.layout:
            for pos in row:
                flat_positions.append(pos)
        
        unique_positions = sorted(set(pos for pos in flat_positions if pos > 0))
        
        try:
            position_index = unique_positions.index(position)
            if position_index < len(self.cards):
                return self.cards[position_index]
        except ValueError:
            pass
        
        return None
    
    def generate_guidance(self) -> list[str]:
        """Generate interpretation guidance using semantic analysis."""
        if not self.analyzer:
            return []
        
        semantic_groups = self.get_semantic_groups()
        return self.analyzer.generate_guidance(self.cards, semantic_groups)
    
    def get_analysis(self) -> dict[str, Any]:
        """Get detailed semantic analysis of the reading."""
        if not self.analyzer:
            return {}
        
        return self.analyzer.analyze_card_combinations(self.cards)
    
    def render_full_interpretation(self, include_keywords: bool = False) -> str:
        """Render complete interpretation including semantic legend and guidance.
        
        Args:
            include_keywords: Whether to include card keywords in legend
            
        Returns:
            Formatted interpretation string
        """
        parts = []
        
        # Add semantic legend
        legend = self.render_semantic_legend(include_keywords)
        if legend:
            parts.append(legend)
        
        # Add guidance if available
        guidance = self.generate_guidance()
        if guidance:
            if parts:  # Add separator if legend exists
                parts.append("\n\n## Interpretive Guidance")
            else:
                parts.append("## Interpretive Guidance")
            parts.extend(guidance)
        
        # Add detailed analysis if available
        analysis = self.get_analysis()
        if analysis:
            if parts:  # Add separator
                parts.append("\n\n## Reading Analysis")
            else:
                parts.append("## Reading Analysis")
            
            # Key insights from analysis
            if analysis.get('major_arcana_count', 0) > analysis.get('minor_arcana_count', 0):
                parts.append("- **Spiritual Focus**: More Major Arcana cards suggest spiritual/karmic themes")
            
            if analysis.get('reversed_count', 0) > len(self.cards) // 2:
                parts.append("- **Transformation Phase**: Many reversed cards indicate change and reflection")
            
            elemental = analysis.get('elemental_balance', {})
            dominant_elements = [elem for elem, count in elemental.items() if count > 0]
            if len(dominant_elements) == 1:
                element_names = {
                    'fire': 'Fire (Action/Passion)',
                    'water': 'Water (Emotion/Intuition)', 
                    'air': 'Air (Intellect/Communication)',
                    'earth': 'Earth (Material/Practical)'
                }
                parts.append(f"- **Elemental Focus**: {element_names.get(dominant_elements[0], dominant_elements[0])}")
        
        return "\n".join(parts)


class TarotDivination:
    """Main orchestrator for tarot divination."""

    def __init__(self, deck_path: str | None = None) -> None:
        self.deck = Deck(deck_path)

    def create_seed(self, timestamp: str, question: str, invocation: str|None = None, random_bytes: int = 0) -> int:
        """Create seed from timestamp, question, optional invocation, and random bytes."""
        seed_data = f"{timestamp}{question}"
        if invocation:
            seed_data += f"|{invocation}"  # Use | as separator
        if random_bytes > 0:
            random_suffix = token_bytes(random_bytes).hex()
            seed_data += random_suffix

        return int.from_bytes(sha256(seed_data.encode()).digest(), 'little')

    def _normalize_spread_layout(self, spread_layout: list[list[int]] | list[int]) -> tuple[list[list[int]], int]:
        """Normalize spread layout to matrix format and return (layout, card_count)."""
        # Handle both list[int] and list[list[int]] cases
        if not spread_layout:
            normalized_layout: list[list[int]] = []
        elif isinstance(spread_layout[0], int):
            # This is a linear layout like [1, 2, 3], convert to [[1, 2, 3]]
            # Type assertion: we know this is list[int] due to isinstance check
            linear_layout = cast(list[int], spread_layout)
            normalized_layout = [linear_layout]
        else:
            # Already in matrix format
            # Type assertion: we know this is list[list[int]] due to isinstance check
            normalized_layout = cast(list[list[int]], spread_layout)
        
        needed_cards = len([pos for row in normalized_layout for pos in row if pos > 0])
        return normalized_layout, needed_cards

    def draw_cards_for_reading(self, seed: int, spread_layout: list[list[int]] | list[int], allow_reversed: bool = False) -> list[Card]:
        """Draw cards for reading using explicit seed - pure deterministic function."""
        rng = DeterministicRNG(seed)
        self.deck.shuffle_and_assign_reversals(rng, allow_reversed)

        _, needed_cards = self._normalize_spread_layout(spread_layout)
        return self.deck.draw_cards(needed_cards)

    def perform_reading_json(self, question: str, spread_layout: list[list[int]] | list[int], invocation: str|None = None,
                            random_bytes: int = 0, allow_reversed: bool = False, include_legend: bool = True) -> dict[str, Any]:
        """Perform tarot reading and return JSON-serializable data."""
        # Create seed and draw cards (reuse existing logic)
        timestamp = str(int(time()))
        seed = self.create_seed(timestamp, question, invocation, random_bytes)
        drawn_cards = self.draw_cards_for_reading(seed, spread_layout, allow_reversed)

        # Normalize layout and generate JSON structure
        normalized_layout, _ = self._normalize_spread_layout(spread_layout)
        json_data = SpreadRenderer.render_json(drawn_cards, normalized_layout, include_legend)

        # Add metadata
        json_data.update({
            "question": question,
            "spread_type": str(spread_layout),
            "timestamp": timestamp,
            "seed": seed,
            "allow_reversed": allow_reversed,
            "invocation": invocation  # Add invocation to metadata
        })

        return json_data

    def perform_reading(self, question: str, spread_layout, invocation: str|None = None,
                        random_bytes: int = 0, allow_reversed: bool = False, show_descriptions: bool = True, spread_type: str = "unknown") -> tuple[str, str]:
        """Perform complete tarot reading by orchestrating seed creation, card drawing, and formatting."""
        # Create seed
        timestamp = str(int(time()))
        seed = self.create_seed(timestamp, question, invocation, random_bytes)

        # Draw cards
        drawn_cards = self.draw_cards_for_reading(seed, spread_layout, allow_reversed)

        # Format output
        normalized_layout, _ = self._normalize_spread_layout(spread_layout)
        spread_display = SpreadRenderer.render_spread(drawn_cards, normalized_layout)

        # Get semantics for named spreads, empty for custom layouts
        semantics = SEMANTICS.get(spread_type, None)
        legend_display = SpreadRenderer.render_semantic_legend(drawn_cards, normalized_layout, semantics, include_keywords=show_descriptions)

        return spread_display, legend_display

    def perform_reading_enhanced(self, question: str, spread_input: str, invocation: str|None = None,
                                 random_bytes: int = 0, allow_reversed: bool = False, show_descriptions: bool = True) -> tuple[str, str, dict[str, Any]]:
        """Perform enhanced tarot reading with semantic analysis support.
        
        Returns:
            Tuple of (spread_display, legend_display, analysis_data)
        """
        # Resolve spread with semantic configuration
        layout, semantic_config = resolve_spread_with_semantics(spread_input)
        
        # Create seed
        timestamp = str(int(time()))
        seed = self.create_seed(timestamp, question, invocation, random_bytes)

        # Draw cards
        drawn_cards = self.draw_cards_for_reading(seed, layout, allow_reversed)

        # Format output
        normalized_layout, _ = self._normalize_spread_layout(layout)
        spread_display = SpreadRenderer.render_spread(drawn_cards, normalized_layout)

        # Use enhanced semantic adapter
        adapter = SemanticAdapter(normalized_layout, drawn_cards, None, semantic_config)
        legend_display = adapter.render_semantic_legend(include_keywords=show_descriptions)
        
        # Generate analysis data
        analysis_data = {
            'semantic_groups': adapter.get_semantic_groups(),
            'guidance': adapter.generate_guidance(),
            'analysis': adapter.get_analysis(),
            'semantic_config': semantic_config
        }

        return spread_display, legend_display, analysis_data


def resolve_spread(spread_input: str) -> list[list[int]]:
    """Resolve spread from alias, custom file, or custom matrix."""
    # Check built-in spreads first
    if spread_input in SPREADS:
        return SPREADS[spread_input]
    
    # Try to load custom spread
    loader = SpreadLoader()
    custom_spread = loader.load_spread(spread_input)
    if custom_spread and 'layout' in custom_spread:
        return custom_spread['layout']
    
    # Try to parse as custom matrix
    try:
        return ast.literal_eval(spread_input)
    except (ValueError, SyntaxError):
        raise ValueError(f"Invalid spread '{spread_input}'. Use aliases: {list(SPREADS.keys())}, custom spread name, or custom matrix.")


def resolve_spread_with_semantics(spread_input: str) -> tuple[list[list[int]], dict[str, Any]|None]:
    """Resolve spread with semantic configuration from alias, custom file, or custom matrix.
    
    Returns:
        Tuple of (layout, semantic_config)
    """
    # Check built-in spreads first
    if spread_input in SPREADS:
        return SPREADS[spread_input], None
    
    # Try to load custom spread
    loader = SpreadLoader()
    custom_spread = loader.load_spread(spread_input)
    if custom_spread and 'layout' in custom_spread:
        layout = custom_spread['layout']
        semantic_config = {k: v for k, v in custom_spread.items() if k != 'layout'}
        return layout, semantic_config
    
    # Try to parse as custom matrix
    try:
        layout = ast.literal_eval(spread_input)
        return layout, None
    except (ValueError, SyntaxError):
        raise ValueError(f"Invalid spread '{spread_input}'. Use aliases: {list(SPREADS.keys())}, custom spread name, or custom matrix.")


def resolve_card_codes(codes: str) -> list[Card]:
    """Resolve CSV card codes to Card objects."""
    if not codes:
        return []

    # Split CSV and clean whitespace
    code_list = [code.strip() for code in codes.split(',') if code.strip()]

    # Create a temporary deck for card lookup
    deck = Deck()
    card_dict = {}

    # Create lookup dictionary
    for card in deck.cards:
        code = card.get_notation_code()
        card_dict[code] = card

    resolved_cards = []
    for code in code_list:
        # Handle reversal notation like [↓XVI]
        is_reversed = False
        if code.startswith('[↓') and code.endswith(']'):
            is_reversed = True
            code = code[2:-1].strip()  # Remove [↓ and ]
        elif code.startswith('[ ') and code.endswith(']'):
            code = code[2:-1].strip()  # Remove [ and ]

        # Clean up common notation issues
        # Convert underscore notation (C_Q) to direct notation (CQ)
        if '_' in code and len(code) == 3 and code[1] == '_':
            code = code[0] + code[2]

        # Look up the card
        if code in card_dict:
            card = card_dict[code]
            # Create a copy and set reversal if needed
            resolved_card = Card(card.name, card.card_type, card.suit, card.value, card.keywords, card.reversed_keywords, is_reversed)
            resolved_cards.append(resolved_card)
        else:
            raise ValueError(f"Invalid card code: '{code}'. Valid codes include major arcana (I, II, etc.) and minor arcana (W3, CQ, SA, PK, etc.)")

    return resolved_cards


def create_parser() -> ArgumentParser:
    """Create command line argument parser."""
    parser = ArgumentParser(description="Tarot divination script")
    parser.add_argument("question", nargs='?', help="Question for tarot reading (ignored with --lookup and --list-decks)")
    parser.add_argument("--lookup", help="Look up card codes (CSV format, e.g., 'I,W3,C_Q,XVII')")
    parser.add_argument("--invocation", help="Custom invocation to influence reading")
    parser.add_argument("--invoke", action="store_true",
                       help="Use default invocation to influence reading (By the wisdom of Hermes-Thoth and foresight of Prometheus)")
    parser.add_argument("--spread", default="3-card",
                       help=f"Spread layout (default: 3-card). Available: {list(SPREADS.keys())} or custom matrix")
    parser.add_argument("--random", type=int, default=8,
                       help="Add N random bytes to RNG seed for entropy (default: 8)")
    parser.add_argument("--no-keywords", action="store_true",
                       help="Hide card keyword descriptions (shown by default)")
    parser.add_argument("--reversed", action="store_true",
                       help="Allow cards to appear reversed")
    parser.add_argument("--json", action="store_true",
                       help="Output reading in JSON format")
    parser.add_argument("--deck", help="Use custom deck configuration filename")
    parser.add_argument("--list-decks", action="store_true",
                       help="List available deck configurations")
    return parser


def get_invocation_text(args) -> str|None:
    """Get invocation text from command line arguments."""
    if args.invocation:
        return args.invocation
    elif args.invoke:
        # Default invocation for --invoke flag
        return """
By the wisdom of Hermes-Thoth, guide of souls and keeper of sacred knowledge,
and by the foresight of Prometheus, bringer of fire and divine insight, I seek
understanding through the ancient art of tarot."""[1:]
    else:
        return None


def main(args=None) -> int:
    """Main CLI interface."""
    parser = create_parser()

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    # Handle list-decks mode
    if args.list_decks:
        deck_loader = DeckLoader()
        decks = deck_loader.list_available_decks()
        if not decks:
            print(f"No deck configurations found in {config.decks_dir}/")
            return 0

        print("Available decks:")
        for deck in decks:
            filename = deck['filename']
            name = deck['name']
            description = deck['description']
            print(f"  {filename:<20} - {name:<20} - {description}")
        return 0

    # Handle lookup mode
    if args.lookup:
        try:
            cards = resolve_card_codes(args.lookup)
        except ValueError as e:
            print(f"Error: {e}")
            return 1

        if args.json:
            # JSON output for lookup
            json_data = SpreadRenderer.render_legend_json(cards, include_keywords=True)
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        else:
            # ASCII output for lookup
            legend_display = SpreadRenderer.render_legend(cards, include_keywords=True)
            print(legend_display)

        return 0

    # Resolve deck path if specified
    deck_path = None
    if args.deck:
        deck_loader = DeckLoader()
        deck_path = deck_loader.resolve_deck_path(args.deck)
        if not deck_path:
            print(f"Error: Deck file '{args.deck}' not found. Searched:")
            print(f"  ./{args.deck}")
            print(f"  ./{args.deck}.json")
            print(f"  {config.decks_dir}/{args.deck}")
            print(f"  {config.decks_dir}/{args.deck}.json")
            return 1

    # Validate that question is provided for reading mode
    if not args.question:
        print("Error: Question is required for tarot reading. Use --lookup to look up card codes or --list-decks to see available decks.")
        return 1

    try:
        spread_layout = resolve_spread(args.spread)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Get invocation from arguments
    invocation = get_invocation_text(args)

    try:
        tarot = TarotDivination(deck_path)
    except ValueError as e:
        print(f"Error loading deck: {e}")
        return 1

    if args.json:
        # JSON output path
        json_data = tarot.perform_reading_json(args.question, spread_layout, invocation, args.random, args.reversed, include_legend=True)
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
    else:
        # ASCII output path
        spread_display, legend_display = tarot.perform_reading(args.question, spread_layout, invocation, args.random, args.reversed, not args.no_keywords, args.spread)
        print(f"Question: {args.question}")
        if invocation:
            print(f"Reading influenced by divine invocation")
        print(f"Spread: {args.spread}\n")
        print(spread_display)
        print("\n" + legend_display)

    return 0


if __name__ == '__main__':
    exit(main())
