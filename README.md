# Brainhack-BLT2-backend

# API Endpoint

https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging

# Available APIs

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations`

- GET: Get the information about all the sports facilities in the app database
- POST: Add a new entry about a sports facility to the database

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations/<string:regionName>`

- GET: Get the information about all the sports facilities in the specified region in the app database

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations/<string:regionName>/<string:locationId>`

- GET: Get the information about the sports facility in the specified region with the specified location ID in the app database
