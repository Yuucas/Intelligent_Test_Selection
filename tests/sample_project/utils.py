"""
Utility functions for sample project
"""
from typing import List, Any, Dict, Optional
import re


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    # Remove special characters
    return re.sub(r'[<>\"\'%;()&+]', '', text)


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (part / total) * 100


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:.2f}"


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def is_palindrome(text: str) -> bool:
    """Check if text is palindrome"""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return cleaned == cleaned[::-1]


def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_query_string(query: str) -> Dict[str, str]:
    """Parse URL query string"""
    if not query:
        return {}

    params = {}
    for param in query.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            params[key] = value
    return params


def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string"""
    if not params:
        return ''
    return '&'.join([f"{k}={v}" for k, v in params.items()])


class StringFormatter:
    """String formatting utilities"""

    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convert to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def to_camel_case(text: str) -> str:
        """Convert to camelCase"""
        components = text.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def to_pascal_case(text: str) -> str:
        """Convert to PascalCase"""
        components = text.split('_')
        return ''.join(x.title() for x in components)

    @staticmethod
    def to_kebab_case(text: str) -> str:
        """Convert to kebab-case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
