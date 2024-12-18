import requests
import json
import time
import os
from datetime import datetime
from settings import ONEMAP_KEY
from settings import load_jsonfile, save_jsonfile, json_file
from database import session_pool
from models import Location
from models import PostalCode
from models import OneMapResponse
from api import Api
from misc_tools import wait_some_seconds
import logging
import sys

_DEBUG = False
if _DEBUG:
  level=logging.DEBUG
else:
  level=logging.INFO

logFormatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
rootLogger = logging.getLogger()

# fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler = logging.FileHandler("pull_onemap.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(level)

if not os.path.exists('singapore_addresses.db'):
  import create_schema
  logging.info("Creating schema...")

headers = {"Authorization": ONEMAP_KEY}

url = "https://www.onemap.gov.sg/api/common/elastic/search"

params = {
    'searchVal'     : "000001",
    'returnGeom'    : "Y",
    'getAddrDetails': "N",
    'pageNum'       : 1
}

limited_display = lambda s : s if len(s) < 40 else s[:37]+'...'
last_counter = 0
try:
  logging.info(f"Reading '{json_file}'...")
  start, end = load_jsonfile()
except TypeError:
  start = 1
  end = 10000
  if not os.path.exists(json_file):
    raise

def main():
  global start, end, last_counter
  logging.info(f"XX{start:04d} to XX{end-1:04d}")

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
    # wait_some_seconds(2, True)
    for i in range(1, 100):
      last_counter = j
      postal_code = f"{i:02d}{j:04d}"
      # keep status updated on screen
      print(f"\r{datetime.now()} | {postal_code}", end='')
      # wait_some_seconds(3)   # Throttling effect
      print('\r', end='')
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
            logging.info(f"Failed at {postal_code}")
            break
          else:
            logging.info(f" {postal_code} |"
              f" {16*'-'} |"
              f" {16*'-'} |"
              f" {'---'}")
            continue
        try:
          r = json.loads(response)
        except json.JSONDecodeError as e:
          with open('onemap_error.log', 'a') as fp:
            fp.write(f"{datetime.now()}: {str(e)}\n{response}\n\n")
            fp.close()
          # logging.info(f"{str(e): '{postal_code}'}")
          logging.info(f" {postal_code} |"
            f" {16*'-'} |"
            f" {16*'-'} |"
            f"  {0:2d}/{0:2d}  |"
            f" {str(e)}")
          continue
        r = json.loads(response)
        current_page = r['pageNum']
        total_pages =  r['totalNumPages']
        record_count = r['found']
        if not record_count:
          if current_page <= total_pages:
            current_page += 1
          continue

        else:
          for index, row in enumerate(r['results']):
            record_index  = (r['pageNum']-1)*10 + index+1
            latitude      = row['LATITUDE']
            longitude     = row['LONGITUDE']
            # Create a session from the sessionmaker
            with session_pool() as session:
              # Query for the location where postal_code, page_number and name matches DB
              record = session.query(Location).filter(
                  Location.postal_code == postal_code,
                  Location.latitude    == latitude,
                  Location.longitude   == longitude,
                  Location.name        == row['SEARCHVAL']).all()
              location = False if len(record) == 0 else record[0]

              oneMapEntry = session.query(OneMapResponse).filter(
                OneMapResponse.postal_code  == postal_code,
                OneMapResponse.total_pages  == total_pages,
                OneMapResponse.total_records== record_count,
                OneMapResponse.response     == response
                ).one_or_none()

              if location and oneMapEntry:
                logging.info(f" {postal_code} |"
                      f" [{location.latitude:1.12f}] |"
                      f" [{location.longitude:3.10f}] |"
                      f" [{record_index:2d}/{record_count:2d}] |"
                      f" {limited_display(location.name)}")
                continue

              logging.info(f" {postal_code} |"
                    f"  {latitude[:14]:14s}  |"
                    f"  {longitude[:14]:14s}  |"
                    f"  {record_index:2d}/{record_count:2d}  |"
                    f" {limited_display(row['SEARCHVAL'])}")

              counter += 1
              newLocation = Location(
                name        = row['SEARCHVAL'],
                postal_code = postal_code,
                latitude    = latitude,
                longitude   = longitude,
                )
              session.add(newLocation)

              if oneMapEntry is None:
                newResponse = OneMapResponse(
                  total_pages   = total_pages,
                  page_number   = current_page,
                  total_records = record_count,
                  postal_code   = postal_code,
                  response      = response
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
        #   logging.info(f"{params['searchVal']} | {r['found']:2d} |    |")
      # Set the api object to the original state.
      # This will prevent the pageNum from incurring unnecessary iterations
      api.sets(**params)
      api.set('pageNum', 1)
  # display(Markdown('---'))
  end_time = time.time()
  hh = int(end_time-start_time) // 3600
  mm = int(end_time-start_time) % 3600 // 60
  ss = int(end_time-start_time) % 60
  record_insertion_speed = counter / (end_time-start_time)

  logging.info(f"{counter} records added.")
  logging.info(f"Duration: {hh:02d}:{mm:02d}:{ss:02d}. Rate: {record_insertion_speed:.3f} records per sec.")
  if fail_counter == max_failure:
    raise KeyboardInterrupt


if __name__=='__main__':
  try:
    main()
  except KeyboardInterrupt:
    raise
  finally:
    if not _DEBUG:
      start = last_counter
      save_jsonfile([start, end])
      logging.info(f"\nStart updated to {start}")
