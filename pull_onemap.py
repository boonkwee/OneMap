import requests
import json
import time
from settings import ONEMAP_KEY
from database import session_pool
from models import Location
from models import PostalCode
# from IPython.display import Markdown, display

headers = {"Authorization": ONEMAP_KEY}

url = "https://www.onemap.gov.sg/api/common/elastic/search"

params = {
    'searchVal'     : "000001",
    'returnGeom'    : "Y",
    'getAddrDetails': "N",
    'pageNum'       : "1"
}

# insert new locations record
start_time = time.time()
char_count = 0
counter = 0

for j in range(1, 1001):
  for i in range(1, 100):
    # wait_some_seconds()   # Throttling effect
    postal_code = f"{i:02d}{j:04d}"
    params['searchVal'] = postal_code
    response = requests.request("GET", url, headers=headers, params=params)
    try:
      r = json.loads(response.text)
    except json.JSONDecodeError as e:
      print(f"{str(e)}: [{response.text}]")
      continue
    r = json.loads(response.text)
    if r['found']:
      for index, row in enumerate(r['results']):
        # Create a session from the sessionmaker
        with session_pool() as session:
          # Query for the location where postal_code, page_number and name matches DB
          existing_records = session.query(Location).filter(
              Location.postal_code==postal_code,
              Location.page_number==index+1,
              Location.name==row['SEARCHVAL']).all()
          if existing_records:
            record = existing_records[0]
            display_str = f"{params['searchVal']} | {r['found']:2d} | {r['totalNumPages']:2d} | {record.page_number} | [{record.latitude:1.14f}] | [{record.longitude:3.12f}] | {record.name}"
            continue
          else:
            display_str = f"{params['searchVal']} | {r['found']:2d} | {r['totalNumPages']:2d} | {index+1} | {row['LATITUDE']:16s} | {row['LONGITUDE']:16s} | {row['SEARCHVAL']}"
          print(display_str)
          char_count += len(display_str)

          counter += 1
          newLocation = Location(name=row['SEARCHVAL'],
                                latitude=r['results'][0]['LATITUDE'],
                                longitude=r['results'][0]['LONGITUDE'],
                                total_pages=r['found'],
                                page_number=index+1)
          session.add(newLocation)

          # check if postal code already exist in PostalCode, if not exist insert new Postal code
          postalCode = session.query(PostalCode).filter(PostalCode.postal_code==postal_code).one_or_none()
          if postalCode is None:
            newPostalCode = PostalCode(postal_code=postal_code)
            session.add(newPostalCode)
            newLocation.postal_code_index = newPostalCode
          else:
            newLocation.postal_code_index = postalCode
          session.commit()
  #  else:
  #    print(f"{params['searchVal']} | {r['found']:2d} |    |")
# display(Markdown('---'))
end_time = time.time()
hh = int(end_time-start_time) // 3600
mm = int(end_time-start_time) % 3600 // 60
ss = int(end_time-start_time) % 60
record_insertion_speed = (end_time-start_time) / counter

print(f"{counter} records added; {char_count} characters. ", end='')
print(f"Duration: {hh:02d}:{mm:02d}:{ss:02d}. Rate: {record_insertion_speed:.3f} records per sec.")
