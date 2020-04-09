#!/usr/local/bin/python3
import subprocess
import sys
import json
import time
import requests
import random

SAMPLE_SIZE = 10000
POISSON_LAMBDA = 3.25
# Edit this URL if you create your own cloud function
clear_shelves_url = 'Your-GCP-url-/clear_shelves'

with open('../../../resources/orders.json', 'r') as f:
    orders = json.load(f)

# Clear shelves to begin experiment
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(clear_shelves_url, headers=headers)
time.sleep(1)

# Dispatch orders
for i in range(SAMPLE_SIZE):
  random_order = random.randrange(0,len(orders)-1)
  current_order = orders[random_order]
  data = (orders[random_order])
  order_id = i
  json_args = '{"name": "' + data["name"] + '","order_id": "' + str(order_id) + '", "temp": "' + data["temp"] + '", "shelfLife": "' + str(data["shelfLife"]) + '", "decayRate": "' + str(data["decayRate"]) + '"}'
  call = "python3 post.py \'" + json_args + "\'&"
  subprocess.call(call, shell=True)
  time.sleep(random.expovariate(POISSON_LAMBDA))
