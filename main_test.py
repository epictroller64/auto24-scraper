
import curl_cffi
from services.parser_service import Auto24ParserService
import json
from structures.Auto24Listing import ListingPreview
from rich import print


### Test scraper outputs
headers={
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Referer": "https://www.auto24.ee/bmw"
}

def test_vehicle_details():
    listings_resp = curl_cffi.get("https://www.auto24.ee/kasutatud/nimekiri.php?b=4&ae=8&bw=244&f2=2010&f1=2003", headers=headers, impersonate="chrome")
    listings_resp.raise_for_status()
    prelistings = Auto24ParserService().parse_prelistings(listings_resp.text)
    listing_resp = curl_cffi.get("https://www.auto24.ee/soidukid/4078081", headers=headers, impersonate="chrome")
    listing_resp.raise_for_status()
    details = Auto24ParserService().parse_vehicle_details(listing_resp.text, prelistings[0])
    print(details)

test_vehicle_details()
