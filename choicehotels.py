from datetime import date
from datetime import timedelta
import urllib2
import json
from lxml import html
import re

BASE_URL = "https://www.choicehotels.com/webapi/hotel/%s/rates"
BASE_FORM_DATA = "adults=1&checkInDate=%s&checkOutDate=%s&clientId=SKq4ExZrseK2&currencyCode=HOTEL_DEFAULT_CURRENCY&include=relative_media%%2C%%20component_room_descriptions&includePackages=false&includePromotions=false&minors=0&preferredLanguageCode=EN&ratePlans=NGGL%%2CRACK%%2CPREPD&rateType=LOW_RACK&rooms=1&viewType=ALL"

class Choice(object):
    def __init__(self, name, id):
        self.ID = id
        self.NAME = name

    def LowestRateForStay(self, start_date, end_date):
      lowest_rate = 999999
      lowest_room = None
      url = BASE_URL % (self.ID,)
      form_data = BASE_FORM_DATA % (start_date, end_date)
      handler=urllib2.HTTPHandler()
      opener = urllib2.build_opener(handler)
      request = urllib2.Request(url, form_data)
      request.add_header("Content-Type", "application/x-www-form-urlencoded")
      request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")
      content = opener.open(request).read()
      rate_response = json.loads(content)
      
      if rate_response.has_key('stay'):
        #print json.dumps(rate_response['stay'], indent=3)
        # print json.dumps(rate_response['rooms'], indent=3)
        for room in rate_response['stay']['rates'].values():
          for rate in room['roomStayCharges']:
            room = rate_response['rooms'][rate["roomCode"]]["bedsDescription"]
            rate = float(rate["afterTax"])
            if rate < lowest_rate:        
              lowest_rate = rate
              lowest_room = room

        if lowest_rate == 999999:  
          return None
        else:
          return (lowest_room, lowest_rate)

hotel = Choice("Castlereagh", "AU852")
hotel = Choice("Hotel Harry", "AU763")

# Single Night Lowest Rate
if (False):
  for i in range(12,18):
    startdate = date.today() + timedelta(i)
    enddate = startdate + timedelta(1)
    print str(startdate) + ": " + str(hotel.LowestRateForStay(startdate, enddate))

