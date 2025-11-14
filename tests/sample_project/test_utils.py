"""
Tests for utility functions
"""
import pytest
from .utils import (
    validate_email, sanitize_string, calculate_percentage,
    format_currency, chunk_list, flatten_dict, merge_dicts,
    remove_duplicates, is_palindrome, truncate_string,
    parse_query_string, build_query_string, StringFormatter
)


class TestEmailValidation:
    """Test cases for email validation"""

    def test_valid_email(self):
        """Test valid email"""
        assert validate_email('test@example.com') is True

    def test_invalid_email_no_at(self):
        """Test invalid email without @"""
        assert validate_email('testexample.com') is False

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain"""
        assert validate_email('test@') is False

    def test_invalid_email_no_tld(self):
        """Test invalid email without TLD"""
        assert validate_email('test@example') is False


class TestStringSanitization:
    """Test cases for string sanitization"""

    def test_sanitize_clean_string(self):
        """Test sanitizing clean string"""
        result = sanitize_string('Hello World')
        assert result == 'Hello World'

    def test_sanitize_special_chars(self):
        """Test sanitizing special characters"""
        result = sanitize_string('Hello<script>alert("xss")</script>')
        assert '<' not in result
        assert '>' not in result

    def test_sanitize_sql_chars(self):
        """Test sanitizing SQL characters"""
        result = sanitize_string("'; DROP TABLE users--")
        assert "'" not in result
        assert ';' not in result


class TestPercentageCalculation:
    """Test cases for percentage calculation"""

    def test_calculate_percentage_normal(self):
        """Test normal percentage calculation"""
        result = calculate_percentage(25, 100)
        assert result == 25.0

    def test_calculate_percentage_zero_total(self):
        """Test percentage with zero total"""
        result = calculate_percentage(25, 0)
        assert result == 0.0

    def test_calculate_percentage_decimal(self):
        """Test percentage with decimals"""
        result = calculate_percentage(33.33, 100)
        assert result == 33.33


class TestCurrencyFormatting:
    """Test cases for currency formatting"""

    def test_format_usd(self):
        """Test USD formatting"""
        result = format_currency(100.50, 'USD')
        assert result == '$100.50'

    def test_format_eur(self):
        """Test EUR formatting"""
        result = format_currency(100.50, 'EUR')
        assert result == '€100.50'

    def test_format_gbp(self):
        """Test GBP formatting"""
        result = format_currency(100.50, 'GBP')
        assert result == '£100.50'

    def test_format_unknown_currency(self):
        """Test unknown currency defaults to $"""
        result = format_currency(100.50, 'XYZ')
        assert result == '$100.50'


class TestChunkList:
    """Test cases for chunking list"""

    def test_chunk_list_even(self):
        """Test chunking evenly divisible list"""
        result = chunk_list([1, 2, 3, 4, 5, 6], 2)
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_chunk_list_uneven(self):
        """Test chunking unevenly divisible list"""
        result = chunk_list([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_list_empty(self):
        """Test chunking empty list"""
        result = chunk_list([], 2)
        assert result == []


class TestFlattenDict:
    """Test cases for flattening dictionary"""

    def test_flatten_nested_dict(self):
        """Test flattening nested dictionary"""
        nested = {'a': {'b': {'c': 1}}}
        result = flatten_dict(nested)
        assert result == {'a.b.c': 1}

    def test_flatten_flat_dict(self):
        """Test flattening already flat dictionary"""
        flat = {'a': 1, 'b': 2}
        result = flatten_dict(flat)
        assert result == flat

    def test_flatten_custom_separator(self):
        """Test flattening with custom separator"""
        nested = {'a': {'b': 1}}
        result = flatten_dict(nested, sep='_')
        assert result == {'a_b': 1}


class TestMergeDicts:
    """Test cases for merging dictionaries"""

    def test_merge_two_dicts(self):
        """Test merging two dictionaries"""
        result = merge_dicts({'a': 1}, {'b': 2})
        assert result == {'a': 1, 'b': 2}

    def test_merge_overlapping_keys(self):
        """Test merging with overlapping keys"""
        result = merge_dicts({'a': 1}, {'a': 2})
        assert result == {'a': 2}

    def test_merge_multiple_dicts(self):
        """Test merging multiple dictionaries"""
        result = merge_dicts({'a': 1}, {'b': 2}, {'c': 3})
        assert result == {'a': 1, 'b': 2, 'c': 3}


class TestRemoveDuplicates:
    """Test cases for removing duplicates"""

    def test_remove_duplicates_with_dupes(self):
        """Test removing duplicates"""
        result = remove_duplicates([1, 2, 2, 3, 3, 3])
        assert result == [1, 2, 3]

    def test_remove_duplicates_no_dupes(self):
        """Test list without duplicates"""
        result = remove_duplicates([1, 2, 3])
        assert result == [1, 2, 3]

    def test_remove_duplicates_preserves_order(self):
        """Test that order is preserved"""
        result = remove_duplicates([3, 1, 2, 1, 3])
        assert result == [3, 1, 2]


class TestPalindrome:
    """Test cases for palindrome checking"""

    def test_is_palindrome_true(self):
        """Test palindrome string"""
        assert is_palindrome('racecar') is True

    def test_is_palindrome_false(self):
        """Test non-palindrome string"""
        assert is_palindrome('hello') is False

    def test_is_palindrome_with_spaces(self):
        """Test palindrome with spaces"""
        assert is_palindrome('A man a plan a canal Panama') is True

    def test_is_palindrome_mixed_case(self):
        """Test palindrome with mixed case"""
        assert is_palindrome('RaceCar') is True


class TestTruncateString:
    """Test cases for string truncation"""

    def test_truncate_long_string(self):
        """Test truncating long string"""
        result = truncate_string('Hello World', 8)
        assert result == 'Hello...'

    def test_truncate_short_string(self):
        """Test string shorter than limit"""
        result = truncate_string('Hello', 10)
        assert result == 'Hello'

    def test_truncate_custom_suffix(self):
        """Test truncating with custom suffix"""
        result = truncate_string('Hello World', 8, suffix='…')
        assert result == 'Hello W…'


class TestQueryString:
    """Test cases for query string operations"""

    def test_parse_query_string(self):
        """Test parsing query string"""
        result = parse_query_string('key1=value1&key2=value2')
        assert result == {'key1': 'value1', 'key2': 'value2'}

    def test_parse_empty_query_string(self):
        """Test parsing empty query string"""
        result = parse_query_string('')
        assert result == {}

    def test_build_query_string(self):
        """Test building query string"""
        result = build_query_string({'key1': 'value1', 'key2': 'value2'})
        assert 'key1=value1' in result
        assert 'key2=value2' in result

    def test_build_empty_query_string(self):
        """Test building empty query string"""
        result = build_query_string({})
        assert result == ''


class TestStringFormatter:
    """Test cases for StringFormatter"""

    def test_to_snake_case(self):
        """Test converting to snake_case"""
        assert StringFormatter.to_snake_case('CamelCase') == 'camel_case'
        assert StringFormatter.to_snake_case('camelCase') == 'camel_case'

    def test_to_camel_case(self):
        """Test converting to camelCase"""
        assert StringFormatter.to_camel_case('snake_case') == 'snakeCase'

    def test_to_pascal_case(self):
        """Test converting to PascalCase"""
        assert StringFormatter.to_pascal_case('snake_case') == 'SnakeCase'

    def test_to_kebab_case(self):
        """Test converting to kebab-case"""
        assert StringFormatter.to_kebab_case('CamelCase') == 'camel-case'
        assert StringFormatter.to_kebab_case('camelCase') == 'camel-case'
