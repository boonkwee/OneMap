import requests
import json
import time
import os
from settings import ONEMAP_KEY
from settings import load_jsonfile, save_jsonfile, json_file
from database import session_pool
from models import Location
from models import PostalCode
from models import OneMapResponse
from api import Api

headers = {"Authorization": ONEMAP_KEY}

url = "https://www.onemap.gov.sg/api/common/elastic/search"

params = {
    'searchVal'     : "000001",
    'returnGeom'    : "Y",
    'getAddrDetails': "N",
    'pageNum'       : 1
}

last_counter = 0
try:
  print(f"Reading '{json_file}'...")
  start, end = load_jsonfile()
except TypeError:
  start = 1
  end = 10000
  if not os.path.exists(json_file):
    raise

def main():
  global start
  global end
  global last_counter
  print(f"XX{start:04d} to XX{end-1:04d}")

  # api = Api(url=url, method='GET', param=params, header=headers)
  api = Api(url=url, method='GET', param=params)
  # insert new locations record
  start_time = time.time()
  counter = 0
  max_failure = 1
  fail_counter = 0

  for j in range(start, end):
    if fail_counter == max_failure:
      break
    for i in range(1, 100):
      last_counter = j
      # wait_some_seconds()   # Throttling effect
      postal_code = f"{i:02d}{j:04d}"
      api.set('searchVal', postal_code)
      # refresh the current_page and total_pages from api
      total_pages = api.get('pageNum')
      current_page = api.get('pageNum')
      while current_page <= total_pages:
        api.set('pageNum', current_page)
        try:
          response = api.call()
        except requests.exceptions.ConnectionError:
          fail_counter += 1
          if fail_counter == max_failure:
            print(f"Failed at {postal_code}")
            break
          else:
            print(f"{postal_code} |"
                  f" {16*'-'} |"
                  f" {16*'-'} |"
                  f" {'---'}")
            continue
        try:
          r = json.loads(response.text)
        except json.JSONDecodeError as e:
          print(f"{str(e)}: [{response.text}]")
          continue
        r = json.loads(response.text)
        current_page = r['pageNum']
        total_pages =  r['totalNumPages']
        record_count = r['found']
        if not record_count:
          if current_page <= total_pages:
            current_page += 1
          continue

        else:
          for index, row in enumerate(r['results']):
            record_index = (r['pageNum']-1)*10 + index+1
            # Create a session from the sessionmaker
            with session_pool() as session:
              # Query for the location where postal_code, page_number and name matches DB
              record = session.query(Location).filter(
                  Location.postal_code==postal_code,
                  Location.name==row['SEARCHVAL']).one_or_none()
              if record:
                print(f"{postal_code} |"
                      f" [{record.latitude:1.12f}] |"
                      f" [{record.longitude:3.10f}] |"
                      f" [{record_index:2d}] |"
                      f" {record.name}")
                continue

              print(f"{postal_code} |"
                    f" {row['LATITUDE']:16s} |"
                    f" {row['LONGITUDE']:16s} |"
                    f"  {record_index:2d}  |"
                    f" {row['SEARCHVAL']}")

              counter += 1
              newLocation = Location(
                name=row['SEARCHVAL'],
                postal_code=postal_code,
                latitude=r['results'][index]['LATITUDE'],
                longitude=r['results'][index]['LONGITUDE'],
                )
              session.add(newLocation)

              oneMapEntry = session.query(OneMapResponse).filter(
                OneMapResponse.postal_code==postal_code,
                OneMapResponse.total_pages==total_pages,
                OneMapResponse.total_records==record_count,
                OneMapResponse.response==response.text
                ).one_or_none()

              if oneMapEntry is None:
                newResponse = OneMapResponse(
                  total_pages=total_pages,
                  page_number=current_page,
                  total_records=record_count,
                  postal_code=postal_code,
                  response=response.text
                )
                session.add(newResponse)

              # check if postal code already exist in PostalCode, if not exist insert new Postal code
              postalCode = session.query(PostalCode).filter(PostalCode.postal_code==postal_code).one_or_none()
              if postalCode is None:
                newPostalCode = PostalCode(postal_code=postal_code)
                session.add(newPostalCode)
                newLocation.postal_code_index = newPostalCode
                newResponse.postal_code_index = newPostalCode
              else:
                newLocation.postal_code_index = postalCode
              session.commit()
          if current_page <= total_pages:
            current_page += 1
        # else:
        #   print(f"{params['searchVal']} | {r['found']:2d} |    |")
      # Set the api object to the original state.
      # This will prevent the pageNum from incurring unnecessary iterations
      api.sets(**params)
  # display(Markdown('---'))
  end_time = time.time()
  hh = int(end_time-start_time) // 3600
  mm = int(end_time-start_time) % 3600 // 60
  ss = int(end_time-start_time) % 60
  record_insertion_speed = counter / (end_time-start_time)

  print(f"{counter} records added. ", end='')
  print(f"Duration: {hh:02d}:{mm:02d}:{ss:02d}. Rate: {record_insertion_speed:.3f} records per sec.")
  if fail_counter == max_failure:
    raise KeyboardInterrupt


if __name__=='__main__':
  try:
    main()
  except KeyboardInterrupt:
    start = last_counter
    save_jsonfile([start, end])
    print(f"Start updated to {start}")
    input("Enter any key to continue...")
    raise
