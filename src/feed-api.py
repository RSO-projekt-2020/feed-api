from flask import *
from flask_cors import CORS
import datetime
from os import environ
import requests
import string
import random

# logging imports
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter


route = '/v1'
app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})
app.config['USERS_API_URI'] = 'http://users-api:8080/v1' # environ['USERS_API_URI'] 
app.config['VIDEOS_API_URI'] = 'http://videos-api:8080/v1' # environ['VIDEOS_API_URI']

# -------------------------------------------
# Logging setup
# -------------------------------------------
# Create the logger and set it's logging level
logger = logging.getLogger("logstash")
logger.setLevel(logging.INFO)        

log_endpoint_uri = str(environ["LOGS_URI"]).strip()
log_endpoint_port = int(environ["LOGS_PORT"].strip())


# Create the handler
handler = AsynchronousLogstashHandler(
    host=log_endpoint_uri,
    port=log_endpoint_port, 
    ssl_enable=True, 
    ssl_verify=False,
    database_path='')

# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter()
handler.setFormatter(formatter)

# Assign handler to the logger
logger.addHandler(handler)

print("Uri: " + log_endpoint_uri)
print("PORT: " + str(log_endpoint_port))


# functions
def public_feed(request_id):
    response = request.get(app.config['VIDEOS_API_URI'] + '/videos/list', headers={'X-Request-ID': request_id})
    return [x for x in response.json()['content']]


def private_feed(token, user_id, request_id):
    user_response = requests.get(app.config['USERS_API_URI'] + '/follow', headers={'Authorization': token, 'X-Request-ID': request_id})
    following = user_response.json()['following']
    feed = []
    for id in following:
        id = id['user_id']
        video_response = requests.get(app.config['VIDEOS_API_URI'] + '/videos/list/{}'.format(id), headers={'X-Request-ID': request_id})
        feed.extend(video_response.json()['content'])
    feed.sort(reverse=True, key=lambda x: x['created_on'])
    return feed


def generate_request_id():
    return ''.join(random.choice(string.ascii_letters) for x in range(10))
 

# views
@app.route(route + '/feed', methods=['GET'])
def feed():
    request_id = generate_request_id() 
    feed = []
    if 'Authorization' not in request.headers.keys():
        feed = public_feed(request_id)
    else:
        token = request.headers.get('Authorization')
        user_id = requests.get(app.config['USERS_API_URI'] + '/user/check', headers={'Authorization': token, 'X-Request-ID': request_id}).json()['user_id']
        feed = private_feed(token, user_id, request_id)
    logger.info("200 - OK - id:" + request_id)

    return make_response({'msg': 'ok', 'feed': feed}) 


@app.route(route + '/mejnik', methods=['GET'])
def mejnik():
    out = {"clani": ["lk2633", "ks2411"],
            "opis_projekta": "Nas projekt imitira aplikacijo Instagram.",
            "mikrostoritve": ["http://20.62.245.206:8080/v1/user/1", "http://20.62.246.87:8080/v1/videos/list"],
            "github": ["https://github.com/RSO-projekt-2020/users-api", "https://github.com/RSO-projekt-2020/videos-api", "https://github.com/RSO-projekt-2020/feed-api"],
            "travis": ["https://github.com/RSO-projekt-2020/users-api/actions", "https://github.com/RSO-projekt-2020/videos-api/actions", "https://github.com/RSO-projekt-2020/feed-api/actions"],
            "dockerhub": ["https://hub.docker.com/r/klemenstanic/users-api", "https://hub.docker.com/r/klemenstanic/video-api", "https://hub.docker.com/r/klemenstanic/feed-api"],
        }
    logger.info("200 - OK")
    return make_response(out)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
