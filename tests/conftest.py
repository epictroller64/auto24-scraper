import pytest
from services.auto24_scraper_service import Auto24ScraperService
from services.network_service import NetworkService
from services.parser_service import Auto24ParserService

@pytest.fixture
def scraper_service():
    return Auto24ScraperService()

@pytest.fixture
def network_service():
    return NetworkService()

@pytest.fixture
def parser_service():
    return Auto24ParserService() 