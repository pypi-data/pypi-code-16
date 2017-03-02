#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
try:
    from .packages.crawlib.urlencoder import BaseUrlEncoder
except:
    from crawl_zillow.packages.crawlib.urlencoder import BaseUrlEncoder


class UrlEncoder(BaseUrlEncoder):
    domain = "https://www.redfin.com"
    
    def state_listpage(self):
        """
        
        Example: https://www.redfin.com/states
        """
        return "https://www.redfin.com/states"
    
    def city_listpage(self, state_href, prefix):
        """
        
        Example: https://www.redfin.com/states/MD?cities=A
        """
        prefix = prefix.upper()
        if prefix not in string.ascii_uppercase:
            raise ValueError("'prefix' has to be A - Z!")
        return self.url_join("{state_href}/?cities={prefix}".format(
            state_href=state_href, prefix=prefix))
    
    def house_listpage_csv(self, 
                           region_id, 
                           house_type_code=None, 
                           sold_within_days=36500,
                           returns=10000):
        """
        
        Example: https://www.redfin.com/stingray/api/gis-csv?al=1&market=dc&num_homes=100&ord=redfin-recommended-asc&page_number=1&region_id=7974&region_type=6&sf=1,2,3,4,5,6,7&sold_within_days=365&sp=true&status=9&uipt=2&v=8
        """
        if house_type_code is None:
            house_type_code = [1, 2, 3, 4, 5, 6]
        
        if isinstance(house_type_code, (list, tuple)):
            house_type_code = ",".join([str(i) for i in house_type_code])
        else:
            house_type_code = str(house_type_code)
            
        return "https://www.redfin.com/stingray/api/gis-csv?al=1&market=dc&num_homes={returns}&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type=6&sf=1,2,3,4,5,6,7&sold_within_days={sold_within_days}&sp=true&status=9&uipt={house_type_code}&v=8".format(
            returns=returns,
            region_id=region_id, 
            sold_within_days=sold_within_days, 
            house_type_code=house_type_code,
        )

urlencoder = UrlEncoder()

if __name__ == "__main__":
    import webbrowser
    from crawl_redfin.const.house_type import house_type_collection
    
    def test_all():
#         webbrowser.open(urlencoder.state_listpage())
#         webbrowser.open(urlencoder.city_listpage("/states/MD", "A"))
        
        url = urlencoder.house_listpage_csv(
            7974, 
            house_type_collection.name____Condo.id, 
            sold_within_days=365, 
            returns=100,
        )
        print(url)
        
    test_all()