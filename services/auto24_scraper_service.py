
from services.network_service import NetworkService
from services.parser_service import Auto24ParserService
from structures import Pagination


class Auto24ScraperService:
    def __init__(self) -> None:
        self.network_service = NetworkService()
        self.base_url = "https://auto24.ee"

    async def scrape_all_listings(self):
        """
        Scrape all the listings with their preview details.
        """
        def get_path(page_num: int):
            ak = (page_num - 1) * 50
            path = f"kasutatud/nimekiri.php?bn=2&a=100&ae=8&af=50&otsi=otsi&ak={str(ak)}"
            return path

        all_prescraped_listings = []
        listings, pagination = await self.scrape_prelistings(get_path(1))
        all_prescraped_listings.extend(listings)
        for i in range(pagination.current_page + 1, pagination.max_page):
            listings, pagination = await self.scrape_prelistings(get_path(i))
            all_prescraped_listings.extend(listings)
        return all_prescraped_listings
        
    async def scrape_vehicle_details(self, path: str):
        """
        Scrape vehicle details for further processing.
        """
        url = f"{self.base_url}{path}"
        response_text = await self.network_service.get_request(url)
        vehicle_details = Auto24ParserService.
        
    async def scrape_prelistings(self, path: str):
       response_text = await self.network_service.get_request(self.get_url(path))
       if not response_text:
           raise Exception("Failed to scrape: " + path)
       prelistings = Auto24ParserService().parse_prelistings(response_text)
       pagination = self.determine_pagination(response_text)
       return prelistings, pagination

    def determine_pagination(self, response_text: str):
        pagination = Auto24ParserService().parse_pagination(response_text)
        return pagination

    def get_url(self, path: str):
        return f'{self.base_url}/{path}'
