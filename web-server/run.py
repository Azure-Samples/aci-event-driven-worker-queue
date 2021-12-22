#!/usr/bin/env python

from config.config import queueConf, DATABASE_URI, ACI_CONFIG, azure_context
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.amqp import AmqpAnnotatedMessage
from azure.mgmt.monitor import MonitorManagementClient
from flask import Flask, render_template, request, Response
import json
from pymongo import MongoClient
from bson.json_util import dumps
import requests
import random
import traceback


# TODO: Use Azure's sentiment analysis tool to perform everything



#The monitor client to get container group metrics
monitor_client = MonitorManagementClient(azure_context.credentials, azure_context.subscription_id)

#set up the service bus queue
servicebus_client = ServiceBusClient.from_connection_string(conn_str=queueConf['connstr'])

#Connect to the databases
client = MongoClient(DATABASE_URI + "&ssl=true")
db = client.containerstate

#Preset respones
SUCCESS = Response(json.dumps({'success':True}), status=200, mimetype='application/json')

# News api template, find documentation at https://newsapi.org
NEW_API_URL_TEMPLATE = "https://newsapi.org/v2/everything?q={key_word}&sortBy=publishedAt&apiKey={api_key}&page={page}&pageSize=100"


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# Add work to the service bus queue to be picked up by the queue watcher
@app.route('/sendwork', methods=['POST'])
def sendwork():
    work = request.get_json()['work']
    name = _getRandomName()

    db.containerstate.insert_one({"name":name, "state":"Pending"})

    print("Creating job with work: ", work)

    try:
        sender = servicebus_client.get_queue_sender(queue_name=queueConf['queue_name'])
        value_body = {b"name": name, "body": work}
        value_message = AmqpAnnotatedMessage(value_body=value_body)
        sender.send_messages(value_message)
        # sender.send_messages(ServiceBusMessage(name=name,body=work))
    except:
        db.containerstate.update_one({"name":name},{"$set":{"state":"Error","message":traceback.format_exc()}})
    
    return SUCCESS

def _getRandomName():
    baseName = ["anders", "wenjun", "robbie", "robin", "allen", "tony", "xiaofeng", "tingting", "harry", "chen"]
    length = len(baseName)
    name = baseName[int(random.random() * length)]

    baseSuffix = "abcdefghijklmnopqrstuvwxyz0123456789"
    length = len(baseSuffix)
    suffix = "-"
    for i in range(5):
        suffix += baseSuffix[int(random.random() * length)]
    return name + suffix

# Clear the database of the current state
@app.route('/clear', methods=['PUT'])
def clear():
    print("clearing database")
    dict = {}
    container_names = db.containerstate.find({})
    for item in container_names:
        key = item['name']
        if key not in dict:
            sender = servicebus_client.get_queue_sender(queue_name=queueConf['delete_queue_name'])
            sender.send_messages(ServiceBusMessage(key))
            dict[key] = True
    db.containerstate.delete_many({})
    return SUCCESS


# Check the databases for the current state of container groups
@app.route('/currentstate', methods=['GET'])
def current_state():
    #Get all container states
    container_states = db.containerstate.find({})

    current_states = []

    #Convert to list of state objects
    for item in container_states:
        state = item.get('state')
        output = item.get('output')
        if state == "Error":
            output = item.get('message')
        current_states.append({
            "name": item.get('name'),
            "state": state,
            "output": output
        })

    return json.dumps({"container_states": current_states})


# Dumb the actual contents of the databases for debugging
@app.route('/admin/currentdbstate', methods=['GET'])
def current_db_state():
    db_state = db.containerstate.find({})
    return dumps({"db_state": list(db_state)})


# Get a sentiment analysis based on a passed in keyword
@app.route('/api/sentiment/<key_word>', methods=['GET'])
def get_sentiment_analysis(key_word):
    # Get the news articles about the key word from the api
    articles = _getNewsArticlesWithKeyword(key_word)
    
    # Perform sentiment analysis on either the title or description
    for article in articles:
        article["title"]
        article["description"]

    # TODO: Use Azure's sentiment analysis tool to perform everything 

# Need to page through the api response. Only 1000 requests per day so only pull 
#   4 pages for each key word
def _getNewsArticlesWithKeyword(key_word):
    # Get inital first 100 results then use totalResults to find the page splits
    
    articles = []

    # NOTE: Depending on the keyword, there might not be 99 pages
    #   This wont error but just wont return anything
    for i in [1, 25, 75, 99]:
        url = NEW_API_URL_TEMPLATE.format(key_word = key_word, api_key = News_api_key, page = i)
        resp = GetAPIResponse(url)
        if not resp:
            return Response(json.dumps({'success':False}), status=500, mimetype='application/json')

        articles.append(resp['articles'])

    return articles


# Show the available metrics for the container group, should always be MemoryUsage and CPUUsage
@app.route('/api/availablemetrics/<container_name>', methods=['GET'])
def available_metrics(container_name):
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/microsoft.containerinstance/containerGroups/{}"
    ).format(ACI_CONFIG['subscriptionId'], ACI_CONFIG['resourceGroup'], container_name)

    metrics = monitor_client.metric_definitions.list(resource_id)

    available_metrics = [ metric.name.value for metric in metrics]

    return json.dumps({"available_metrics": available_metrics})


# Get the container group metrics for a specific container
@app.route('/api/metrics/<container_name>', methods=['GET'])
def get_metrics(container_name):
    metrics = _get_metrics(ACI_CONFIG['subscriptionId'], ACI_CONFIG['resourceGroup'], container_name)

    return json.dumps({"chartData": metrics})


def _get_metrics(subscription_id, resource_group_name, container_name):
    resource_id = (
        "subscriptions/{}/"
        "resourceGroups/{}/"
        "providers/microsoft.containerinstance/containerGroups/{}"
    ).format(subscription_id, resource_group_name, container_name)

    #filter = " and ".join(["name.value"])CpuUsage,MemoryUsage

    labels = []
    series_labels = []
    data_points = []
    
    metrics_data = monitor_client.metrics.list(resource_id,metricnames="CpuUsage,MemoryUsage")
    for item in metrics_data.value:
        data = list()
        series_label = list()

        labels.append(item.name.localized_value)

        for data_point in item.timeseries[0].data:
            data.append(NoneZero(data_point.average))
            series_label.append(data_point.time_stamp.strftime('%H:%M:%S'))

        series_labels.append(series_label)
        data_points.append(data)

    return {
        "labels": labels,
        "seriesLabels": series_labels,
        "dataPoints": data_points
    }


# Convert Nones to 0 for graphing correctly
def NoneZero(val):
    if val is None:
        return 0
    else:
        return val

# Get a json API response
def GetAPIResponse(url):
    try:
        response = requests.get(url)
    except Exception as e:
        print('Failed to get from URL: ' + str(e))
        return False

    if(response == None):
        print('GetAPIResponse: No Request')
        return False

    if(response.status_code != 200):
        print('GetAPIResponse: Non 200 status code of ' +
                     str(response.status_code))
        return False

    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,threaded=True)