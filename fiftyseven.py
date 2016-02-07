from datetime import date
from datetime import timedelta
import urllib2
import json

startdate = date.today()
BASE_RATE_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_rates?check_in_date=%s&check_out_date=%s&locale=en&promotion_code=10off"
BASE_ROOM_URL = "https://www.thebookingbutton.com.au/api/v2/reloaded/properties/57hoteldirect/room_types?check_in_date=%s&check_out_date=%s"

def LowestRateForRoomOnNight(room_id, start_date):
  end_date = start_date + timedelta(1)
  return LowestRateForRoomForStay(room_id, start_date, end_date)

def DoesRoomResponseIndicateAvailable(room):
  available = True
  #print json.dumps(room, indent=3)
  for roomdate in room["room_type_dates"]:
    available &= roomdate["available"] > 0
    # print str(roomdate) + " - " + str(roomdate["available"] > 0)
  return available

def FetchRoomAvailability(start_date, end_date):
  url = BASE_ROOM_URL % (start_date, end_date)
  response = urllib2.urlopen(url)
  html = response.read()
  return json.loads(html)
    
def RoomIsAvailableForStay(room_id, start_date, end_date):
  for room in FetchRoomAvailability(room_id, start_date, end_date):
    if room['id'] in (room_id,):
      return DoesRoomResponseIndicateAvailable(room)
  return False    
    
def LowestRateForRoomForStay(room_id, start_date, end_date, known_available=False):
  lowest_rate = 999999

  
  if known_available or RoomIsAvailableForStay(room_id, start_date, end_date):
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

def LowestRateForStay(start_date, end_date):
  lowest_rate = 999999
  lowest_room = None
  for room in FetchRoomAvailability(start_date, end_date):
      if DoesRoomResponseIndicateAvailable(room):
        rate = LowestRateForRoomForStay(room["id"], start_date, end_date, known_available=True)
        if rate is not None and rate < lowest_rate:
            lowest_rate = rate
            lowest_room = room["name"]
        
  if lowest_rate == 999999:  
    return None
  else:
    return (lowest_room, lowest_rate)


def LowestRatesForSubspansOfLength(start_date, end_date, length):
    while start_date + timedelta(length) <= end_date:
        span_end = start_date + timedelta(length)
        best_span = LowestRateForStay(start_date, span_end)
        #print "Best span of length %s %s (%s days): %s" % (start_date, span_end, length, best_span)
        yield (start_date, span_end, best_span)
        start_date = start_date + timedelta(1)

def LowestRatesForSubspans(start_date, end_date):
    #print "Lowest rates from: %s-%s" % (start_date, end_date)
    days_covered = (end_date - start_date).days
    for length in range(days_covered, 0, -1):
        #print "Getting spans of length %s" % (length,)
        for x in LowestRatesForSubspansOfLength(start_date, end_date, length):
          yield x
   
def ListDiff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]

def ListIntersection(a, b):
    b = set(b)
    return [aa for aa in a if aa in b]
            
def FindBinPackings(startdate, enddate, lowest_rates, stays_so_far=None, nights_needed=None, nights_covered=None):
    if nights_needed is None:
        nights_needed = [startdate + timedelta(days=x) for x in range(0, (enddate - startdate).days)]
    if nights_covered is None:
        nights_covered = set()
    if stays_so_far is None:
        stays_so_far = list()
        
    if nights_needed:
      for subspan in lowest_rates:
          nights_in_subspan = [subspan[0] + timedelta(days=x) for x in range(0, (subspan[1] - subspan[0]).days)]
          overlap = ListIntersection(nights_covered, nights_in_subspan)
          #print "Checking subspan %s against nights_needed %s" % (nights_in_subspan, nights_needed)
          if (overlap):
              # print "Not adding, it overlaps"
              pass
          else:
              nights_needed_after_subspan = ListDiff(nights_needed, nights_in_subspan)
              #print "Looks good, will still need %s" % (nights_needed_after_subspan,)
              new_stays_so_far = list(stays_so_far)
              new_stays_so_far.append(subspan)
              new_nights_covered = set(nights_covered)
              new_nights_covered.update(nights_in_subspan)
              for x in FindBinPackings(startdate, enddate, lowest_rates, new_stays_so_far, nights_needed_after_subspan, new_nights_covered):
                  yield x
    else:
        #print "Complete span %s" % stays_so_far
        yield sorted(stays_so_far, key=lambda foo: foo[0])

def BinPacks(startdate, enddate, lowest_rates_for_subspans):
  for packing in FindBinPackings(startdate, enddate, lowest_rates_for_subspans):
    room_changes = len(packing) - 1
    price = sum([x[2][1] for x in packing])
    pretty_stays = ["%s-%s in %s ($%s)" % (x[0], x[1], x[2][0], x[2][1]) for x in packing]
    yield(price, room_changes, pretty_stays)

def BestBinPacks(startdate, enddate, lowest_rates_for_subspans):
    bin_packs = sorted(BinPacks(startdate, enddate, lowest_rates_for_subspans), key=lambda x: (x[0], x[1]))
    last_price = 999999
    last_changes = 99999
    for bin_pack in bin_packs:
        if bin_pack[0] < last_price or bin_pack[1] < last_changes:
            last_price = bin_pack[0]
            last_changes = bin_pack[1]
            yield bin_pack
    
    

# Single Night Test
if (False):
  for i in range(2,4):
    startdate = date.today() + timedelta(i)
    print str(startdate) + ": " + str(LowestRateForRoomOnNight(103576, startdate))
  
# Multi Night Test
if (False):
  for i in range(2,6):
    startdate = date.today() + timedelta(i)
    enddate = date.today() + timedelta(i+3)
    print str(startdate) + "-" + str(enddate) + ": " + str(LowestRateForRoomForStay(103576, startdate, enddate))

# Single Night Lowest Rate
if (False):
  for i in range(2,7):
    startdate = date.today() + timedelta(i)
    enddate = startdate + timedelta(1)
    print str(startdate) + ": " + str(LowestRateForStay(startdate, enddate))

# Find all lowest rates for subspans
if (False):  
  startdate = date.today() + timedelta(8)
  enddate = date.today() + timedelta(11)
  for z in LowestRatesForSubspans(startdate, enddate):
     print z

# Testez le binpacking with fixed data
if (True):
  startdate = date(2016, 2, 15)
  enddate = date(2016, 2, 18)
  lowest_rates_for_subspans = (
  (date(2016, 2, 15), date(2016, 2, 18), (u'Dancing Queen', 732.45)),
  (date(2016, 2, 15), date(2016, 2, 17), (u'57 Single', 305.9)),
  (date(2016, 2, 16), date(2016, 2, 18), (u'Twin Shoebox', 434.15)),
  (date(2016, 2, 15), date(2016, 2, 16), (u'57 Single', 135.85)),
  (date(2016, 2, 16), date(2016, 2, 17), (u'57 Single', 170.05)),
  (date(2016, 2, 17), date(2016, 2, 18), (u'Twin Shoebox', 229.9)),
  )
  print "Finding best solutions for {:%Y-%m-%d}-{:%Y-%m-%d}".format(startdate, enddate)
  for packing in BestBinPacks(startdate, enddate, lowest_rates_for_subspans):
      print "$%s, %s changes: %s" % (packing[0], packing[1], "; ".join(packing[2]))
    