#!/usr/local/bin/python3
import sys
import json
import random
import time
from google.cloud import datastore
datastore_client = datastore.Client()

#Preset Params
OVERFLOW_CAPACITY = 20
SHELF_CAPACITY = 15
# DELIVERY_MIN != DELIVERY_MAX
DELIVERY_MIN = 2
DELIVERY_MAX = 10

class order():
  temp = {"hot","cold","frozen"}
  def __init__(self,order_id,name,temp,shelfLife,decayRate):
    self.order_id = order_id
    self.name = name
    self.temp = temp
    self.shelfLife = shelfLife
    self.decayRate = decayRate
    self.age = 0
    self.value = self.calculate_value()
    self.normalizedValue = self.calculate_normalized_value()

  # Move orders to their preferred shelf if on overflow shelf
  # Subtract value from order as it decays
  def decay(self,shelf):
    overflow_multiplier = 1
    shelf_type = self.temp
    order_key = datastore_client.key(shelf_type,self.order_id)
    if shelf.overflow:
      order_key = shelf.overflow_shuffle()
      if self.value <= 0:
        return
      if shelf.overflow:
        shelf_type = "overflow"
        overflow_multiplier = 2
      else:
        shelf_type = self.temp
        overflow_multiplier = 1
    self.age += 1
    time.sleep(1)
    self.value = self.calculate_value(overflow_multiplier)
    self.normalizedValue = self.calculate_normalized_value()
    shelf.update(order_key)
    print("normalizedValue:" + str(self.normalizedValue))

  def calculate_normalized_value(self):
    return self.value/self.shelfLife

  def calculate_value(self,overflow_multiplier=1):
    return ((self.shelfLife - self.age) - ((self.decayRate * overflow_multiplier) * self.age))

class shelf():
   overflow = False
   def __init__(self,order,capacity):
     self.order = order
     self.capacity = capacity

   # Put order on preferred shelf is space, otherwise put on overflow
   # If no space on overflow, disgard order.
   def put(self):
     shelf_type = self.order.temp
     if self.has_space(shelf_type) == False:
       self.overflow = True
       shelf_type = "overflow"
       if self.has_space("overflow") == False:
         self.order.shelfLife = 0
         return datastore_client.key(shelf_type,self.order.order_id)
     else:
       self.overflow = False
     order_key = datastore_client.key(shelf_type,self.order.order_id)
     order_entity = datastore.Entity(key=order_key)
     order_entity['name'] = self.order.name 
     order_entity['temp'] = self.order.temp
     order_entity['value'] = self.order.normalizedValue
     datastore_client.put(order_entity)
     print(shelf_type+"++")
     return order_key

   def has_space(self,shelf_type):
     query = datastore_client.query(kind=shelf_type)
     if shelf_type == "overflow":
       capacity = OVERFLOW_CAPACITY
     else:
       capacity = SHELF_CAPACITY
     results = list(query.fetch())
     shelf_count = len(results)
     if shelf_count < capacity:
       return True
     else:
       return False
     
   def get(self,key):
     datastore_client.delete(key)

   def update(self,key):
     order_entity = datastore_client.get(key)
     order_entity['name'] = self.order.name 
     order_entity['temp'] = self.order.temp
     order_entity['value'] = self.order.normalizedValue
     datastore_client.put(order_entity)

   def overflow_shuffle(self):
     order_key = datastore_client.key("overflow", self.order.order_id)
     if self.has_space(self.order.temp):
       self.get(order_key)
       order_key = self.put()
       print("shuffle++")
     return order_key

def call_delivery_driver():
  return random.randrange(DELIVERY_MIN,DELIVERY_MAX)

def receive_order(request):
  data = request.get_json()
  new_order = order(data["order_id"],data["name"],data["temp"],int(data["shelfLife"]),float(data["decayRate"]))
  print("Order Number: " + str(new_order.order_id))
  driver_eta = call_delivery_driver()
  new_shelf = shelf(new_order,SHELF_CAPACITY)
  order_key = new_shelf.put()  
  while new_order.calculate_value() > 0 and driver_eta > 0:
    driver_eta = driver_eta - 1
    new_order.decay(new_shelf)
  if new_shelf.overflow:
    order_key = datastore_client.key("overflow",new_order.order_id)
  else:
    order_key = datastore_client.key(new_order.temp,new_order.order_id)
  new_shelf.get(order_key)
  if new_order.calculate_value() > 0:
    print("delivery++")
  else:
    print("discard++")
  return
