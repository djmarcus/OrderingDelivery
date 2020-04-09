import requests
import sys

order = sys.argv[1]
print(order)

# Edit this URL if you create your own cloud function
kitchen_system_url = 'your-gcp-url/kitchenSystem'

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(kitchen_system_url, data=order, headers=headers)

