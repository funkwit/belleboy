from datetime import date
from datetime import timedelta
import urllib2
import json

startdate = date.today()
BASE_RATE_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_rates?check_in_date=%s&check_out_date=%s&locale=en&promotion_code=10off"
BASE_ROOM_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_types?check_in_date=%s&check_out_date=%s"

def LowestRateForRoomOnNight(room_id, start_date):
  end_date = start_date + timedelta(1)
  lowest_rate = 999999

  url = BASE_ROOM_URL % (start_date, end_date)
  response = urllib2.urlopen(url)
  html = response.read()
  room_response = json.loads(html)
  for room in room_response:
    if room['id'] in (room_id,):
      #print json.dumps(room, indent=3)
      available = room["room_type_dates"][0]["available"]

  if available:
    url = BASE_RATE_URL % (start_date, end_date)
    # print url
    response = urllib2.urlopen(url)
    html = response.read()
    rate_response = json.loads(html)
    for room in rate_response:
      if room['room_type_id'] in (room_id,):
        #print json.dumps(room, indent=3)
        rateinfo = room['room_rate_dates'][0]
        # print json.dumps(rateinfo, indent=3)
        if not rateinfo["stop_sell"] and rateinfo['rate'] < lowest_rate:
            lowest_rate = rateinfo['rate']

  if lowest_rate == 999999:  
    return None
  else:
    return lowest_rate


# Single Night Test
for i in range(2,6):
  startdate = date.today() + timedelta(i)
  print str(startdate) + ": " + str(LowestRateForRoomOnNight(103576, startdate))