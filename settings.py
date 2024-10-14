# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ONEMAP_KEY  = os.environ.get("onemap")
NEONDB_HOST = os.environ.get("neondb_host")
NEONDB_UID  = os.environ.get("neondb_uid")
NEONDB_PWD  = os.environ.get("neondb_pwd")
GMAP        = os.environ.get("gmap")

json_file = os.path.splitext(os.path.basename(__file__))[0] + '.json'

def load_jsonfile():
  try:
    with open(json_file, 'r') as fp:
      obj = json.load(fp)
      fp.close()
      obj[1] = obj[1] if obj[1] < 10000 else 10000
  except FileNotFoundError:
    obj = None
  return obj

def save_jsonfile(obj=None):
  try:
    with open(json_file, 'w') as fp:
      json.dump(obj, fp)
      fp.close()
  except FileNotFoundError:
    pass

if __name__=='__main__':
  print(dotenv_path)
  print(json_file)
  if not os.path.exists(json_file):
    print(f"'{json_file}' not found")
  start, end = load_jsonfile()
  print(f"{start} -> {end}")
  save_jsonfile([start, end])