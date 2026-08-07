import pytest

from src.utils.case_converter import camel_case_to_snake_case


class TestCamelCaseToSnakeCase:

    def test_empty_string(self):
        """Тест для пустой строки"""
        assert camel_case_to_snake_case("") == ""

    def test_single_word_lowercase(self):
        """Тест для слова в нижнем регистре"""
        assert camel_case_to_snake_case("hello") == "hello"

    def test_single_word_uppercase(self):
        """Тест для слова в верхнем регистре"""
        assert camel_case_to_snake_case("HELLO") == "hello"

    def test_camel_case(self):
        """Тест для стандартного CamelCase"""
        assert camel_case_to_snake_case("helloWorld") == "hello_world"

    def test_camel_case_multiple_words(self):
        """Тест для camelCaes с несколькими словами"""
        assert camel_case_to_snake_case("helloWorldFooBar") == "hello_world_foo_bar"

    def test_starts_with_upper_case(self):
        """Тест для строки, начинающейся с заглавной буквы"""
        assert camel_case_to_snake_case("Hello") == "hello"

    def test_consecutive_uppercase(self):
        """Тест для строки с последовательными заглавными буквами"""
        assert camel_case_to_snake_case("XMLParser") == "xml_parser"

    def test_last_two_uppsercases(self):
        """Тест для строки, где последние 2 символа заглавные"""
        assert camel_case_to_snake_case("XMLParserResponse") == "xml_parser_response"

    def test_special_characters(self):
        """Тест для строки со специальными символами"""
        assert camel_case_to_snake_case("helloWorld123") == "hello_world123"

    def test_numbers(self):
        """Тест для строки с числами"""
        assert camel_case_to_snake_case("hello123World") == "hello123_world"
