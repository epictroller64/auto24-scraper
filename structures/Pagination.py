from pydantic import BaseModel

class Pagination(BaseModel):
    max_page: int
    current_page: int
    total_vehicles: int
