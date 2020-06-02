import os

import boto3
import uuid

from helper_func import formatDynamoResponse

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
    data_to_send = {}
    
    data_to_send['locationId'] = {'S': uuid.uuid4().hex }
    for attrib_metadata in attrib_list_ex_locationId:
        for attrib_name, attrib_type in attrib_metadata.items():
            data_to_send[attrib_name] = { attrib_type: request.json.get(attrib_name) }

    if not data_to_send['locationId']:
        return jsonify({'error': 'Please provide locationId'}), 400

    response = client.put_item(
        TableName=locations_table,
        Item=data_to_send
    )

    return jsonify(data_to_send)