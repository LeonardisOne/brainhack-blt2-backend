import os

import boto3
import uuid

from helper_func import formatDynamoResponse, getPostRequest
import traceback
#import copy
from datetime import datetime
import pytz

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
    try:
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
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with getting data'}), 500

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
    try:
        response = client.query(
            TableName=future_bookings_table,
            KeyConditionExpression='locationId = :location_id',
            ExpressionAttributeValues={
                ':location_id': {
                    'S': locationId,
                },
            },
        )  
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with getting data'}), 500

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/locations/<string:regionName>/<string:locationId>")
def get_location(regionName, locationId):
    try:
        resp = client.get_item(
            TableName=locations_table,
            Key={
                'region': { 'S': regionName},
                'locationId': { 'S': locationId }
            }
        )
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with getting data'}), 500
    
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'Location does not exist'}), 404
    
    return_response = formatDynamoResponse(item)

    return jsonify(return_response)

@app.route("/locations", methods=["GET"])
def get_locations():
    try:
        response = client.scan(TableName=locations_table)
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with getting data'}), 500

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

    try:
        response = client.put_item(
            TableName=locations_table,
            Item=data_to_send
        )
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with POST request'}), 500

    return jsonify(data_to_send)

@app.route("/users/<string:username>", methods=["GET"])
def get_user_bookings(username):
    try:
        response = client.query(
            TableName=user_bookings_table,
            KeyConditionExpression='username = :userName',
            ExpressionAttributeValues={
                ':userName': {
                    'S': username,
                },
            },
        )
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with getting data'}), 500

    db_entries = response.get('Items')
    
    return_list = []
    return_response = { 'items':return_list }
    for entry in db_entries:
        temp_dict = formatDynamoResponse(entry)
        
        return_list.append(temp_dict)
    
    return jsonify(return_response)

@app.route("/users/<string:username>", methods=["POST"])
def add_booking(username):
    attrib_list = [{'dateTimeSlot': 'S'}, {'locationId': 'S'}]
    booking_info = getPostRequest(request, attrib_list)
    booking_info['username'] = { 'S': username}

    sg_timezone = pytz.timezone('Asia/Singapore')
    sg_time = datetime.now(sg_timezone)
    print(sg_time)

    try:
        dynamodb = boto3.resource('dynamodb')

        future_bookings_table_ref = dynamodb.Table(future_bookings_table)

        #location_booking_info = copy.deepcopy(booking_info)

        #del location_booking_info['username']

        location_booking_info = {'locationId': request.json.get('locationId'), 'dateTimeSlot': request.json.get('dateTimeSlot')}

        maxOccupancy_response = future_bookings_table_ref.get_item(
            Key=location_booking_info,
            ProjectionExpression='maxOccupancy',
        )

        maxOccupancy = maxOccupancy_response['Item']['maxOccupancy']

        update_location_response = future_bookings_table_ref.update_item(
            Key=location_booking_info,
            UpdateExpression="SET bookings = bookings + :val",
            ConditionExpression="bookings < :max",
            ExpressionAttributeValues={
                ':val': 1,
                ':max': maxOccupancy
            },
            ReturnValues="UPDATED_NEW"
        )

        response = client.put_item(
            TableName=user_bookings_table,
            Item=booking_info
        )
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Error with POST request'}), 500

    return jsonify(booking_info)