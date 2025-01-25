import os
from typing import Iterable, Tuple
from google.oauth2 import service_account
from google.cloud import secretmanager, bigquery
import json