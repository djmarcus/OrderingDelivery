from google.cloud import datastore
datastore_client = datastore.Client()

def clear_shelves():
  query = datastore_client.query(kind="overflow")
  results = list(query.fetch())
  for result in results:
    datastore_client.delete(result.key)
  query = datastore_client.query(kind="cold")
  results = list(query.fetch())
  for result in results:
    datastore_client.delete(result.key)
  query = datastore_client.query(kind="frozen")
  results = list(query.fetch())
  for result in results:
    datastore_client.delete(result.key)
  query = datastore_client.query(kind="hot")
  results = list(query.fetch())
  for result in results:
    datastore_client.delete(result.key)

clear_shelves()
