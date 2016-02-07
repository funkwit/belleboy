from datetime import date
from datetime import timedelta
import urllib2
import json
from lxml import html
import re

BASE_URL = "http://www.starwoodhotels.com/fourpoints/rates/room.html?propertyId=%s&rtnId=&arrivalDate=%s&departureDate=%s&iataNumber=&rp=RC%%3ADFRLM%%2CRC%%3APRORLM%%2CSN%%3A299865%%2C&numberOfRooms=1&numberOfAdults=1&numberOfChildren=0"
# 2016-02-11
# 1305


class Starwood(object):
    def __init__(self, name, id):
        self.ID = id
        self.NAME = name
        
    def LowestRateForRoomOnNight(self, room_id, start_date):
      end_date = start_date + timedelta(1)
      return self.LowestRateForRoomForStay(room_id, start_date, end_date)

   
    def LowestRateForRoomForStay(self, room_id, start_date, end_date, known_available=False):
      lowest_rate = 999999

  
      if known_available or self.RoomIsAvailableForStay(room_id, start_date, end_date):
        url = BASE_RATE_URL % (self.ID, start_date, end_date)
        # print url
        handler=urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(handler)
        httplib.HTTPConnection.debuglevel = 1
        request = urllib2.Request(url)
        print request
        html = opener.open(request).read()
        rate_response = json.loads(html)
        for room in rate_response:
          if room['room_type_id'] in (room_id,):
            #print json.dumps(room, indent=3)
            valid_prices = True
            total_price = 0
            for rateinfo in room['room_rate_dates']:
              # print json.dumps(rateinfo, indent=3)
              if rateinfo["stop_sell"]:
                  valid_prices = False
              else:
                  total_price += rateinfo['rate']
              
            if valid_prices and (total_price < lowest_rate):
                lowest_rate = total_price

      if lowest_rate == 999999:  
        return None
      else:
        return lowest_rate

    def LowestRateForStay(self, start_date, end_date):
      lowest_rate = 999999
      lowest_room = None
      url = BASE_URL % (self.ID, start_date, end_date)
      handler=urllib2.HTTPHandler()
      opener = urllib2.build_opener(handler)
      request = urllib2.Request(url)
      request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")
      content = opener.open(request).read()
      tree = html.fromstring(content)
      for result in tree.xpath("//div[@class='resultName']"):
          room = result.xpath("h3/text()")[0]
          rate_blocks = result.xpath("div/ul/li/span[@class='roomRate']/text()")
          #print room
          if (rate_blocks): 
            rate=int(re.sub("[^0-9]", "", rate_blocks[0]))
            if rate < lowest_rate:
                lowest_rate = rate * (end_date - start_date).days
                lowest_room = room
        
      if lowest_rate == 999999:  
        return None
      else:
        return (lowest_room, lowest_rate)

hotel = Starwood("Four Points", 1305)

# Single Night Lowest Rate
if (False):
  for i in range(12,18):
    startdate = date.today() + timedelta(i)
    enddate = startdate + timedelta(1)
    print str(startdate) + ": " + str(hotel.LowestRateForStay(startdate, enddate))

