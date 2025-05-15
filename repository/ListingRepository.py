from curses.ascii import TAB

from database import supabase
from structures.CarListing import CarListing


class ListingRepository:
    TABLE_NAME = "listings"
    def bulk_insert_listings(self, listings: list[CarListing]):
        try:
            result = (
                supabase.table(self.TABLE_NAME)
                .insert(listings)
                .execute()
            )
            return result
        except Exception as e:
            ### Decide what to do with it in the upper level
            return e

    def get_all(self):
        try:
            result = (
                supabase.table(self.TABLE_NAME)
                .select("*")
                .execute()
            )
            return result
        except Exception as e:
            return e
