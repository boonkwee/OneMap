# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ONEMAP_KEY = os.environ.get("onemap")
NEONDB_HOST = os.environ.get("neondb_host")
NEONDB_UID = os.environ.get("neondb_uid")
NEONDB_PWD = os.environ.get("neondb_pwd")
GMAP = os.environ.get("gmap")