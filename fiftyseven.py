from datetime import date
from datetime import timedelta
import urllib2
import json

BASE_RATE_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_rates?check_in_date=%s&check_out_date=%s&locale=en&promotion_code=10off"
BASE_ROOM_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_types?check_in_date=%s&check_out_date=%s"

class FiftySeven(object):
    NAME = "57 Hotel"
    
    def LowestRateForRoomOnNight(self, room_id, start_date):
      end_date = start_date + timedelta(1)
      return self.LowestRateForRoomForStay(room_id, start_date, end_date)

    def DoesRoomResponseIndicateAvailable(self, room):
      available = True
      #print json.dumps(room, indent=3)
      for roomdate in room["room_type_dates"]:
        available &= roomdate["available"] > 0
        # print str(roomdate) + " - " + str(roomdate["available"] > 0)
      return available

    def FetchRoomAvailability(self, start_date, end_date):
      url = BASE_ROOM_URL % (start_date, end_date)
      response = urllib2.urlopen(url)
      html = response.read()
      return json.loads(html)
    
    def RoomIsAvailableForStay(self, room_id, start_date, end_date):
      for room in self.FetchRoomAvailability(start_date, end_date):
        if room['id'] in (room_id,):
          return self.DoesRoomResponseIndicateAvailable(room)
      return False    
    
    def LowestRateForRoomForStay(self, room_id, start_date, end_date, known_available=False):
      lowest_rate = 999999

  
      if known_available or self.RoomIsAvailableForStay(room_id, start_date, end_date):
        url = BASE_RATE_URL % (start_date, end_date)
        # print url
        response = urllib2.urlopen(url)
        html = response.read()
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
      for room in self.FetchRoomAvailability(start_date, end_date):
          if self.DoesRoomResponseIndicateAvailable(room):
            rate = self.LowestRateForRoomForStay(room["id"], start_date, end_date, known_available=True)
            if rate is not None and rate < lowest_rate:
                lowest_rate = rate
                lowest_room = room["name"]
        
      if lowest_rate == 999999:  
        return None
      else:
        return (lowest_room, lowest_rate)


hotel = FiftySeven()

# Single Night Test
if (False):
  for i in range(2,4):
    startdate = date.today() + timedelta(i)
    print str(startdate) + ": " + str(hotel.LowestRateForRoomOnNight(103576, startdate))
  
# Multi Night Test
if (False):
  for i in range(2,6):
    startdate = date.today() + timedelta(i)
    enddate = date.today() + timedelta(i+3)
    print str(startdate) + "-" + str(enddate) + ": " + str(hotel.LowestRateForRoomForStay(103576, startdate, enddate))

# Single Night Lowest Rate
if (False):
  for i in range(2,7):
    startdate = date.today() + timedelta(i)
    enddate = startdate + timedelta(1)
    print str(startdate) + ": " + str(hotel.LowestRateForStay(startdate, enddate))

