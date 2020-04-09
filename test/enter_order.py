import json
import sys
sys.path.append('../src/python/cloud_functions')	
import kitchen_system

class mock_request():
  def __init__(self,json):
    self.json = json
  
  def get_json(self):
    return self.json


def main():
  new_order = {"name": "Pad See Ew","order_id": "4077", "temp": "hot", "shelfLife": "210", "decayRate": "0.72"}
  request = mock_request(new_order)
  kitchen_system.receive_order(request)

if __name__ == "__main__":
  main()
