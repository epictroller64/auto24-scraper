from pydantic import BaseModel
from typing import Optional

"""
Model for initial scraped listing for Auto24 portal. Before processing
"""
class ScrapedListingPreview(BaseModel):
    title: str
    mark: str
    model: str
    model_short: str
    engine: str
    year: str
    price: str
    mileage: str
    fuel_type: str
    gearbox: str
    body: str
    link: str
    drive: str

class ListingPreview(BaseModel):
    title: str
    mark: str
    model: str
    model_short: str
    engine: str
    year: int
    price: int
    mileage: int
    fuel_type: str
    gearbox: str
    body: str
    drive: str
    link: str

class Feature(BaseModel):
    key: str
    value: str


class Consumption(BaseModel):  # assuming you already have this
    city: Optional[float] = None
    highway: Optional[float] = None
    average: Optional[float] = None

class TechnicalDetail(BaseModel):
    seats: Optional[int] = None
    doors: Optional[int] = None
    lenght: Optional[int] = None  # typo? Should be `length`
    width: Optional[int] = None
    height: Optional[int] = None
    empty_mass: Optional[int] = None
    full_mass: Optional[int] = None
    carry_weight: Optional[int] = None
    trailer_with_brakes: Optional[int] = None
    trailer_without_brakes: Optional[int] = None
    wheelbase: Optional[int] = None
    engine_size: Optional[float] = None
    power: Optional[int] = None
    max_speed: Optional[int] = None
    co2: Optional[int] = None
    fuel: Optional[int] = None  # should this be a string?
    consumption: Optional[Consumption] = None
    axles: Optional[int] = None




class ScrapedListing(BaseModel):
   preview: ScrapedListingPreview
   images: list[str]
   type: str
   first_reg: str
   color: str
   technical_details:TechnicalDetail
   features: list[Feature]

   location: str
   original_country: str
   inspection_until: str
   seller_name: str
   description: str


class Listing(BaseModel):
    preview: ListingPreview
    images: list[str]
    type: str
    first_reg_month: int
    first_reg_year: int
    color: str
    technical_details: list[str]
    location: str
    original_country: str
    inspection_until_month: int
    inspection_until_year: int
    seller_name: str
    description: str
