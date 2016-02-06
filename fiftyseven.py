from datetime import date
from datetime import timedelta
import urllib2
import json

startdate = date.today()
BASE_RATE_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_rates?check_in_date=%s&check_out_date=%s&locale=en&promotion_code=10off"
BASE_ROOM_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_types?check_in_date=%s&check_out_date=%s"

for i in range(2,6):
  startdate = date.today() + timedelta(i)
  enddate = startdate + timedelta(1)
  lowest_rate = 999999

  url = BASE_ROOM_URL % (startdate, enddate)
  response = urllib2.urlopen(url)
  html = response.read()
  room_response = json.loads(html)
  for room in room_response:
    if room['id'] in (103576,):
      #print json.dumps(room, indent=3)
      available = room["room_type_dates"][0]["available"]

  if available:
    url = BASE_RATE_URL % (startdate, enddate)
    # print url
    response = urllib2.urlopen(url)
    html = response.read()
    rate_response = json.loads(html)
    for room in rate_response:
      if room['room_type_id'] in (103576,):
        #print json.dumps(room, indent=3)
        rateinfo = room['room_rate_dates'][0]
        # print json.dumps(rateinfo, indent=3)
        if not rateinfo["stop_sell"] and rateinfo['rate'] < lowest_rate:
            lowest_rate = rateinfo['rate']

  if lowest_rate == 999999:  
    print str(startdate) + ": N/A"
  else:
    print str(startdate) + ": " + str(lowest_rate)
