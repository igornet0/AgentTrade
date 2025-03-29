import pytest
from unittest.mock import Mock, patch, call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from apps.data_parser import ParserNews

# Фикстуры
@pytest.fixture
def mock_driver():
    driver = Mock()
    driver.find_element.return_value = Mock(text="test content")
    return driver

@pytest.fixture
def parser(mock_driver):
    return Parser(driver=mock_driver)

# Юнит-тесты с моками
def test_open_page(parser, mock_driver):
    test_url = "https://example.com"
    parser.open_page(test_url)
    mock_driver.get.assert_called_once_with(test_url)

def test_search_element(parser, mock_driver):
    selector = ".content"
    result = parser.search_element(selector)
    
    # Проверяем вызовы ожидания и поиска элемента
    mock_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, selector)
    assert isinstance(result, Mock)

def test_parse_data(parser, mock_driver):
    result = parser.parse_data()
    mock_driver.find_element.assert_called_with(By.CSS_SELECTOR, ".content")
    assert result == "test content"

# Интеграционный тест (требует установки selenium и драйвера)
@pytest.mark.integration
def test_real_browser_flow():
    from selenium import webdriver
    
    with webdriver.Chrome() as driver:
        parser = Parser(driver)
        driver.get("https://example.com")
        
        # Проверяем реальное взаимодействие
        element = parser.search_element("h1")
        assert element.text.lower() == "example domain"
        
        # Проверяем парсинг данных
        data = parser.parse_data()
        assert "example" in data.lower()

# Тест с использованием pytest-selenium
@pytest.mark.usefixtures("selenium")
def test_with_selenium_fixture(selenium):
    parser = Parser(selenium)
    selenium.get("https://example.com")
    element = parser.search_element("h1")
    assert element.text == "Example Domain"

# Тест обработки исключений
def test_element_not_found(parser, mock_driver):
    mock_driver.find_element.side_effect = Exception("Element not found")
    
    with pytest.raises(Exception) as exc_info:
        parser.search_element(".invalid-selector")
    
    assert "Element not found" in str(exc_info.value)