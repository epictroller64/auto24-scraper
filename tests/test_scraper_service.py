import pytest
import os
from aioresponses import aioresponses
from structures import Pagination

@pytest.mark.asyncio
async def test_scrape_prelistings(scraper_service, aioresponses):
    # Mock the network response
    mock_html = os.read_text("tests/test_data/test_prelistings.html")
    aioresponses.get(
        "https://auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&ae=8&af=50&otsi=otsi&ak=0",
        status=200,
        body=mock_html
    )
    
    listings, pagination = await scraper_service.scrape_prelistings("kasutatud/nimekiri.php?bn=2&a=100&ae=8&af=50&otsi=otsi&ak=0")
    
    assert len(listings) > 0
    assert isinstance(pagination, Pagination)
    assert pagination.current_page == 1

@pytest.mark.asyncio
async def test_get_url(scraper_service):
    path = "kasutatud/nimekiri.php?bn=2&a=100&ae=8&af=50&otsi=otsi&ak=0"
    expected_url = "https://auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&ae=8&af=50&otsi=otsi&ak=0"
    assert scraper_service.get_url(path) == expected_url 