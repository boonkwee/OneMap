import requests
import json
import time
from settings import ONEMAP_KEY
from database import session_pool
from models import Location
from models import PostalCode
from models import OneMapResponse
from api import Api
from pipeline import PipeLine
# from IPython.display import Markdown, display
headers = {"Authorization": ONEMAP_KEY}

url = "https://www.onemap.gov.sg/api/common/elastic/search"

params = {
    'searchVal'     : "000001",
    'returnGeom'    : "Y",
    'getAddrDetails': "N",
    'pageNum'       : "1"
}


if __name__=='__main__':
  p = PipeLine()
  api = Api(url=url, method='GET', param=params, header=headers)
  # insert new locations record
  start_time = time.time()
  counter = 0
  max_failure = 1
  f_counter = 0

  for j in range(207, 1001):
    if f_counter == max_failure:
      break
    for i in range(1, 100):
      # wait_some_seconds()   # Throttling effect
      postal_code = f"{i:02d}{j:04d}"
      api.set('searchVal', postal_code)
      try:
        response = api.call()
      except requests.exceptions.ConnectionError:
        f_counter += 1
        if f_counter == max_failure:
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
      if r['found']:
        current_page = r['pageNum']
        total_pages = r['totalNumPages']
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
                    # f" {record.page_number:2d} |"
                    # f" {record.total_pages:2d} |"
                    # f" {record.record_index:2d} |"
                    # f" {record.total_records:2d} |"
                    f" [{record.latitude:1.12f}] |"
                    f" [{record.longitude:3.10f}] |"
                    f" {record.name}")
              continue
            else:
              print(f"{postal_code} |"
                    # f" {current_page:2d} |"
                    # f" {total_pages:2d} |"
                    # f" {record_index:2d} |"
                    # f" {r['found']:2d} |"
                    f" {row['LATITUDE']:16s} |"
                    f" {row['LONGITUDE']:16s} |"
                    f" {row['SEARCHVAL']}")

            counter += 1
            newLocation = Location(name=row['SEARCHVAL'],
                                   postal_code=postal_code,
                                  latitude=r['results'][index]['LATITUDE'],
                                  longitude=r['results'][index]['LONGITUDE'],
                                  # total_pages=r['totalNumPages'],
                                  # page_number=r['pageNum'],
                                  # total_records=r['found'],
                                  # record_index=record_index
                                  )
            newResponse = OneMapResponse(total_pages=r['totalNumPages'],
                                         page_number=r['pageNum'],
                                         total_records=r['found'],
                                         record_index=record_index,
                                         response=response.text
            )
            session.add(newResponse)
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
      # else:
      #   print(f"{params['searchVal']} | {r['found']:2d} |    |")
  # display(Markdown('---'))
  end_time = time.time()
  hh = int(end_time-start_time) // 3600
  mm = int(end_time-start_time) % 3600 // 60
  ss = int(end_time-start_time) % 60
  record_insertion_speed = counter / (end_time-start_time)

  print(f"{counter} records added. ", end='')
  print(f"Duration: {hh:02d}:{mm:02d}:{ss:02d}. Rate: {record_insertion_speed:.3f} records per sec.")
