# OrderingDelivery

This is an example of observability driven development. The application simulates and order delivery system where users enter an online order and it is dispatched for delivery.
System telemetry is what drives application development in a way to capture the most mission-critical service level indicators. 

This system tracks the following:

* order rate
* delivery rate
* delivery times
* shuffle rate
* discard rate
* shelf put rate by shelf

Shelf contents are displayed in the Google Datastore and the normalized value of each order is updated in real time every second.

# System design

There is a dispatch system which reads orders in from a file and submits them to a Google Cloud Function via an HTTP request containing the order details.

Orders are submitted asynchronously in real-time following a poisson distribution with an average of 3.25 orders per second. Each time an order is submitted a cloud function executes until either it is delivered or discarded. The shelves are represented by google datastore collections shared amongst the multiple concurrent cloud functions.

Each cloud function represents an order as it decays in real time. The cloud function factors in the shelf type in determining the rate of decay for the order. Orders on the overflow shelf decay twice as fast as they do on the order's appropriate shelf.

The structured json logs from each cloud function are stored in google stack driver. Many log based metrics are built into cloud functions. Others are custom. These metrics are then exported to a stack driver dashboard where they can be monitored in real time.

These metrics can be used to create alerting policies based on SLOs for the SLIs.

https://cloud.google.com/monitoring/alerts/using-alerting-ui

# Running the application

This application was designed to be run in google cloud. To test the application locally you still need access to the Google Datastore. Create your own or ask the author for access to the one used in this simulation.

https://cloud.google.com/docs/authentication/getting-started

### Install the datastore packages 
`pip3 install --upgrade google-cloud-datastore`

https://cloud.google.com/datastore/docs/reference/libraries#client-libraries-install-python

### Create a test order locally using the Google Datastore printing to standard out
`cd test && python3 enter_order.py`

### Deploying the cloud function

Upload the cloud functions to GCP

https://cloud.google.com/functions/docs/deploying/

* `src/python/cloud_functions/clear_shelves.py`
* `src/python/cloud_functions/kitchen_system.py`
* `src/python/cloud_functions/requirements.txt`

The trigger URLs are what you will need for running your own simulation. See below.

### Running a simulation using cloud functions and the Google Datastore

This is how you run the simulation in a "Production" environment

Edit the scripts' urls to point to your newly deployed cloud functions

* `src/python/scripts/post.py` for the `kitchen_system` cloud function URL
* `src/python/scripts/kitchen_system.py` for the `clear_shelves` cloud function URL

Then run the dispatcher to start submitting orders your cloud functions in real time. 

`cd src/python/scripts && ./dispatcher.py`

### View observability metrics in Stack Driver
To obtain system telemetry Google Stack Driver metrics and dashboards need to be created. Ask the author for access to 
an example google account with this already set up or create your own.

https://cloud.google.com/monitoring/custom-metrics/creating-metrics
