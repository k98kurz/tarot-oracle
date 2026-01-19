#!/usr/bin/env python3

import sys
from argparse import ArgumentParser, Namespace



class RomanConverter:
    """Converts positive integers to Roman numerals using standard subtractive notation."""

    # Value-symbol pairs ordered from largest to smallest for greedy algorithm
    ROMAN_NUMERALS: list[tuple[int, str]] = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]

    MIN_VALUE = 1
    MAX_VALUE = 3999

    @classmethod
    def convert(cls, number: int) -> str:
        """Convert a positive integer to its Roman numeral representation.

        Args:
            number: Positive integer between 1 and 3999 inclusive

        Returns:
            Roman numeral string

        Raises:
            ValueError: If number is outside valid range
        """
        if not cls._is_valid_number(number):
            raise ValueError(f"Number must be between {cls.MIN_VALUE} and {cls.MAX_VALUE}")

        result = []
        remaining = number

        for value, symbol in cls.ROMAN_NUMERALS:
            while remaining >= value:
                result.append(symbol)
                remaining -= value

        return ''.join(result)

    @classmethod
    def _is_valid_number(cls, number: int) -> bool:
        """Check if number is within valid range for Roman numeral conversion."""
        return cls.MIN_VALUE <= number <= cls.MAX_VALUE


def create_parser() -> ArgumentParser:
    """Create command line argument parser for Roman numeral generator."""
    parser = ArgumentParser(description="Generate Roman numerals from positive integers")
    parser.add_argument("--start", type=int, default=1,
                       help=f"Start number (default: 1, min: {RomanConverter.MIN_VALUE})")
    parser.add_argument("--stop", type=int, default=10,
                       help=f"Stop number (default: 10, max: {RomanConverter.MAX_VALUE})")
    return parser


def validate_range(start: int, stop: int) -> None:
    """Validate that start and stop values are within acceptable range."""
    if not RomanConverter._is_valid_number(start):
        raise ValueError(f"Start value must be between {RomanConverter.MIN_VALUE} and {RomanConverter.MAX_VALUE}")

    if not RomanConverter._is_valid_number(stop):
        raise ValueError(f"Stop value must be between {RomanConverter.MIN_VALUE} and {RomanConverter.MAX_VALUE}")

    if start > stop:
        raise ValueError("Start value must be less than or equal to stop value")


def generate_roman_range(start: int, stop: int) -> list[tuple[int, str]]:
    """Generate Roman numeral conversions for a range of numbers."""
    conversions = []
    for number in range(start, stop + 1):
        roman_numeral = RomanConverter.convert(number)
        conversions.append((number, roman_numeral))
    return conversions


def format_output(conversions: list[tuple[int, str]]) -> str:
    """Format conversions as tab-separated 'number:roman' pairs."""
    return '\t'.join(f"{num}:{roman}" for num, roman in conversions)


def main(args: list[str] | None = None) -> int:
    """Main CLI interface for Roman numeral generator."""
    parser = create_parser()

    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)

    try:
        # Validate input range
        validate_range(parsed_args.start, parsed_args.stop)

        # Generate conversions
        conversions = generate_roman_range(parsed_args.start, parsed_args.stop)

        # Format and output
        output = format_output(conversions)
        print(output)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    exit(main())
