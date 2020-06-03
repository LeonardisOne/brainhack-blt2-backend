# Brainhack-BLT2-backend

# API Endpoint

https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging

# Available APIs

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations`

- GET: Get the information about all the sports facilities in the app database

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations/<string:regionName>`

- GET: Get the information about all the sports facilities in the specified region in the app database

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations/<string:regionName>/<string:locationId>/future`

- GET: Get the future bookings information about the specified sports facility

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/locations/<string:regionName>/<string:locationId>`

- GET: Get the information about the sports facility in the specified region with the specified location ID in the app database

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/users/<string:username>`

- GET: Get the list of bookings made by the specified user
- POST: Add a new booking for the user at the specified location
  E.g.

  `{ "locationId": "f70612ac60bd4503a31fd070046b607b", "dateTimeSlot": "2020-06-04 0900" }`

`https://wrm7pj3sz1.execute-api.us-east-1.amazonaws.com/staging/users/<string:username>/delete`

- POST: Delete a booking by the user at the specified date, time and location
  E.g.

  `{ "locationId": "f70612ac60bd4503a31fd070046b607b", "dateTimeSlot": "2020-06-04 0900" }`
