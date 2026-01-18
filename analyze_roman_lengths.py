#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from tarot_oracle.roman_numerals import RomanConverter


def validate_range(start: int, stop: int) -> None:
    """Validate that start and stop values are within acceptable range."""
    if not RomanConverter._is_valid_number(start):
        raise ValueError(f"Start value must be between {RomanConverter.MIN_VALUE} and {RomanConverter.MAX_VALUE}")

    if not RomanConverter._is_valid_number(stop):
        raise ValueError(f"Stop value must be between {RomanConverter.MIN_VALUE} and {RomanConverter.MAX_VALUE}")

    if start > stop:
        raise ValueError("Start value must be less than or equal to stop value")


def create_parser() -> ArgumentParser:
    """Create command line argument parser for Roman numeral length analyzer."""
    parser = ArgumentParser(description="Analyze Roman numeral string lengths")
    parser.add_argument("--start", type=int, default=1,
                       help=f"Start number (default: 1, min: {RomanConverter.MIN_VALUE})")
    parser.add_argument("--stop", type=int, default=3999,
                       help=f"Stop number (default: 3999, max: {RomanConverter.MAX_VALUE})")
    return parser


def analyze_roman_numeral_lengths(start: int, stop: int):
    """Analyze Roman numeral string lengths for specified range."""
    print(f"Analyzing Roman numeral lengths for range {start}-{stop}...")

    max_length = 0
    max_numbers = []
    length_distribution = {}

    # Generate Roman numerals for specified range
    for number in range(start, stop + 1):
        try:
            roman = RomanConverter.convert(number)
            length = len(roman)

            # Track length distribution
            if length not in length_distribution:
                length_distribution[length] = []
            length_distribution[length].append(number)

            # Track maximum length
            if length > max_length:
                max_length = length
                max_numbers = [number]
            elif length == max_length:
                max_numbers.append(number)

        except Exception as e:
            print(f"Error converting {number}: {e}", file=sys.stderr)
            return 1

    # Report results
    print(f"\nMaximum Roman numeral string length: {max_length}")
    print(f"Numbers with maximum length: {max_numbers}")
    print(f"Count: {len(max_numbers)} numbers")

    # Show examples of maximum length numerals
    print(f"\nExamples of {max_length}-character Roman numerals:")
    for i, number in enumerate(max_numbers[:10]):  # Show first 10
        roman = RomanConverter.convert(number)
        print(f"  {number:>4}: {roman}")

    if len(max_numbers) > 10:
        print(f"  ... and {len(max_numbers) - 10} more")

    # Show length distribution
    print(f"\nLength distribution:")
    for length in sorted(length_distribution.keys()):
        count = len(length_distribution[length])
        print(f"  {length} chars: {count} numbers")

    # Show range of maximum length numbers
    if max_numbers:
        print(f"\nRange of numbers with max length: {min(max_numbers)} to {max(max_numbers)}")

    return 0


def main(args=None):
    """Main CLI interface for Roman numeral length analyzer."""
    parser = create_parser()

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    try:
        # Validate input range
        validate_range(args.start, args.stop)

        # Run analysis
        return analyze_roman_numeral_lengths(args.start, args.stop)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    exit(main())
