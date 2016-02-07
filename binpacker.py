from datetime import date
from datetime import timedelta
import fiftyseven

def LowestRatesForSubspansOfLength(hotel, start_date, end_date, length):
    while start_date + timedelta(length) <= end_date:
        span_end = start_date + timedelta(length)
        best_span = hotel.LowestRateForStay(start_date, span_end)
        #print "Best span of length %s %s (%s days): %s" % (start_date, span_end, length, best_span)
        yield (hotel.NAME, start_date, span_end, best_span)
        start_date = start_date + timedelta(1)

def LowestRatesForSubspans(hotel, start_date, end_date):
    #print "Lowest rates from: %s-%s" % (start_date, end_date)
    days_covered = (end_date - start_date).days
    for length in range(days_covered, 0, -1):
        #print "Getting spans of length %s" % (length,)
        for x in LowestRatesForSubspansOfLength(hotel, start_date, end_date, length):
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
          nights_in_subspan = [subspan[1] + timedelta(days=x) for x in range(0, (subspan[2] - subspan[1]).days)]
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
    price = sum([x[3][1] for x in packing])
    pretty_stays = ["%s-%s in %s ($%s)" % (x[1], x[2], x[3][0], x[3][1]) for x in packing]
    yield(x[0], price, room_changes, pretty_stays)

def BestBinPacks(startdate, enddate, lowest_rates_for_subspans):
    bin_packs = sorted(BinPacks(startdate, enddate, lowest_rates_for_subspans), key=lambda x: (x[1], x[2]))
    last_price = 999999
    last_changes = 99999
    for bin_pack in bin_packs:
        if bin_pack[0] < last_price or bin_pack[1] < last_changes:
            last_price = bin_pack[1]
            last_changes = bin_pack[2]
            yield bin_pack
    
hotels = (fiftyseven.FiftySeven(),)

# Find all lowest rates for subspans
if (False):  
  startdate = date.today() + timedelta(8)
  enddate = date.today() + timedelta(11)
  for hotel in hotels:
    for z in LowestRatesForSubspans(hotel, startdate, enddate):
       print z

# Testez le binpacking with fixed data
if (True):
  startdate = date(2016, 2, 15)
  enddate = date(2016, 2, 18)
  lowest_rates_for_subspans = (
  ("57 Hotel", date(2016, 2, 15), date(2016, 2, 18), (u'Dancing Queen', 732.45)),
  ("57 Hotel", date(2016, 2, 15), date(2016, 2, 17), (u'57 Single', 305.9)),
  ("57 Hotel", date(2016, 2, 16), date(2016, 2, 18), (u'Twin Shoebox', 434.15)),
  ("57 Hotel", date(2016, 2, 15), date(2016, 2, 16), (u'57 Single', 135.85)),
  ("57 Hotel", date(2016, 2, 16), date(2016, 2, 17), (u'57 Single', 170.05)),
  ("57 Hotel", date(2016, 2, 17), date(2016, 2, 18), (u'Twin Shoebox', 229.9)),
  )
  print "Finding best solutions for {:%Y-%m-%d}-{:%Y-%m-%d}".format(startdate, enddate)
  for packing in BestBinPacks(startdate, enddate, lowest_rates_for_subspans):
      print "$%s, %s changes: %s" % (packing[1], packing[2], "; ".join(packing[3]))
    