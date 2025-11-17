"""
Utility functions for terminal output formatting
Handles emoji width, ANSI codes, and Unicode characters properly
"""

import re
import unicodedata
from typing import List, Dict


# ANSI escape code pattern
ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text"""
    return ANSI_ESCAPE_PATTERN.sub('', text)


def char_width(char: str) -> int:
    """
    Calculate terminal column width of a single character
    Accounts for emojis, CJK characters, and combining marks
    """
    # Zero-width characters (combining marks)
    if unicodedata.combining(char):
        return 0

    # Control characters
    if unicodedata.category(char) in ('Cc', 'Cf'):
        return 0

    # East Asian Width
    eaw = unicodedata.east_asian_width(char)
    if eaw in ('W', 'F'):  # Wide, Fullwidth
        return 2

    # Emoji detection (most emojis are wide)
    try:
        name = unicodedata.name(char, '')
        if 'EMOJI' in name or char in '🌐🚀💚🎯🔒⚡🧠🎨🆓🌍🛡️🔍📊📄💾📱☁️⭐🎉🤝💻🐛💡📖⚙️🎮📝':
            return 2
    except:
        pass

    # Most other characters (ASCII, Latin, etc.)
    return 1


def visible_width(text: str) -> int:
    """
    Calculate actual terminal width of text
    Accounts for ANSI codes, emojis, and Unicode
    """
    clean = strip_ansi(text)
    return sum(char_width(ch) for ch in clean)


def pad_to_width(text: str, width: int, align: str = 'left', fill: str = ' ') -> str:
    """
    Pad text to specific visible width

    Args:
        text: Text to pad
        width: Target visible width
        align: 'left', 'center', or 'right'
        fill: Character to use for padding

    Returns:
        Padded text
    """
    current_width = visible_width(text)
    padding_needed = width - current_width

    if padding_needed <= 0:
        return text

    if align == 'left':
        return text + (fill * padding_needed)
    elif align == 'right':
        return (fill * padding_needed) + text
    elif align == 'center':
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return (fill * left_pad) + text + (fill * right_pad)

    return text


def create_header(title: str, width: int = 60, char: str = '=') -> str:
    """Create a centered header with proper emoji width"""
    title_width = visible_width(title)
    padding = (width - title_width) // 2

    if padding < 0:
        padding = 0

    return '\n' + (char * width) + '\n' + (' ' * padding) + title + '\n' + (char * width)


def create_box(lines: List[str], width: int = 60) -> str:
    """
    Create a text box with proper emoji alignment

    Args:
        lines: List of text lines to display
        width: Target width for the box

    Returns:
        Formatted box as string
    """
    box = []
    box.append('┌' + '─' * (width - 2) + '┐')

    for line in lines:
        padded = pad_to_width(line, width - 4, align='left')
        box.append('│ ' + padded + ' │')

    box.append('└' + '─' * (width - 2) + '┘')

    return '\n'.join(box)


def format_table_row(columns: List[str], widths: List[int], separator: str = ' │ ') -> str:
    """
    Format a table row with proper column widths

    Args:
        columns: List of column values
        widths: List of column widths
        separator: Column separator

    Returns:
        Formatted row
    """
    padded_cols = []
    for col, width in zip(columns, widths):
        padded_cols.append(pad_to_width(col, width, align='left'))

    return separator.join(padded_cols)


def analyze_width(text: str) -> Dict:
    """
    Analyze text width for debugging

    Returns:
        Dictionary with width analysis
    """
    clean = strip_ansi(text)
    return {
        'raw_length': len(text),
        'clean_length': len(clean),
        'visible_width': visible_width(text),
        'has_ansi': text != clean,
        'characters': [(ch, char_width(ch)) for ch in clean]
    }


if __name__ == '__main__':
    # Test the utilities
    test_lines = [
        "🌐 WebCheck - High-Performance URL Health Checker",
        "⚙️  Concurrency: 30 | Retries: 3 | SSL: True",
        "⏱️  Rate limit: 0.1s + jitter",
    ]

    print("Width Analysis:")
    for line in test_lines:
        analysis = analyze_width(line)
        print(f"\nLine: {line}")
        print(f"  Raw length: {analysis['raw_length']}")
        print(f"  Visible width: {analysis['visible_width']}")

    print("\n" + "="*60)
    print("\nFormatted Box:")
    print(create_box([
        "🌐 WebCheck",
        "⚡ Fast",
        "🧠 Smart",
        "🆓 Free"
    ], width=30))

    print("\nFormatted Header:")
    print(create_header("🌐 WebCheck - URL Health Checker", width=60))
