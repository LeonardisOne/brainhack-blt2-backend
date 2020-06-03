import os

import boto3
import uuid

from helper_func import formatDynamoResponse, getPostRequest

from flask import Flask, jsonify, request
app = Flask(__name__)

attrib_list_ex_locationId = [{'name': 'S'},
    {'address': 'S'},
    {'imageUrl': 'S'},
    {'maxCapacity': 'N'},
    {'currentOccupancy': 'N'},
    {'startTime': 'S'},
    {'endTime': 'S'},
    {'region': 'S'}]

locations_table = os.environ['LOCATIONS_TABLE']
future_bookings_table = os.environ['FUTURE_BOOKINGS_TABLE']
user_bookings_table = os.environ['USER_BOOKINGS_TABLE']
client = boto3.client('dynamodb')

@app.route("/")
def landing():
    return "Landing for Safe Exercise APIs"

@app.route("/locations/<string:regionName>")
def get_locations_for_region(regionName):
    response = client.query(
        TableName=locations_table,
        KeyConditionExpression='#r = :regionName',
        ExpressionAttributeValues={
            ':regionName': {
                'S': regionName,
            },
        },
        ExpressionAttributeNames={
            '#r': 'region'
        },
    )

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/locations/<path:regionWithLocationId>/future")
def get_future_bookings(regionWithLocationId):
    locationId = str(regionWithLocationId).split('/', 1)[1]
    response = client.query(
        TableName=future_bookings_table,
        KeyConditionExpression='locationId = :location_id',
        ExpressionAttributeValues={
            ':location_id': {
                'S': locationId,
            },
        },
    )

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/locations/<string:regionName>/<string:locationId>")
def get_location(regionName, locationId):
    resp = client.get_item(
        TableName=locations_table,
        Key={
            'region': { 'S': regionName},
            'locationId': { 'S': locationId }
        }
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'Location does not exist'}), 404
    
    return_response = formatDynamoResponse(item)

    return jsonify(return_response)

@app.route("/locations", methods=["GET"])
def get_locations():
    response = client.scan(TableName=locations_table)

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/locations", methods=["POST"])
def create_location():
    data_to_send = getPostRequest(request, attrib_list_ex_locationId)
    
    data_to_send['locationId'] = {'S': uuid.uuid4().hex }

    if not data_to_send['locationId']:
        return jsonify({'error': 'Please provide locationId'}), 400

    response = client.put_item(
        TableName=locations_table,
        Item=data_to_send
    )

    return jsonify(data_to_send)

@app.route("/users/<string:username>", methods=["GET"])
def get_user_bookings(username):
    response = client.query(
        TableName=user_bookings_table,
        KeyConditionExpression='username = :userName',
        ExpressionAttributeValues={
            ':userName': {
                'S': username,
            },
        },
    )

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/users/<string:username>", methods=["POST"])
def add_booking(username):
    attrib_list = [{'username': 'S'}, {'dateTimeSlot': 'S'}, {'locationId': 'S'}]
    booking_info = getPostRequest(request, attrib_list)

    response = client.put_item(
        TableName=user_bookings_table,
        Item=booking_info
    )

    del booking_info['username']

    update_location_response = client.update_item(
        TableName=future_bookings_table,
        Key=booking_info,
        UpdateExpression="SET bookings = bookings + :val",
        ExpressionAttributeValues={
            ':val': {
                'N': "1",
            }
        },
        ReturnValues="UPDATED_NEW"
    )

    return jsonify(booking_info)