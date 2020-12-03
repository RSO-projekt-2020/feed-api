from flask import *
import datetime
from os import environ
import requests

route = '/v1'
app = Flask(__name__)
app.config['USERS_API_URI'] = 'http://users-api:8080/v1' # environ['USERS_API_URI'] 
app.config['VIDEOS_API_URI'] = 'http://videos-api:8080/v1' # environ['VIDEOS_API_URI']


# functions
def public_feed():
    response = request.get(app.config['VIDEOS_API_URI'] + '/videos/list')
    return [x for x in response.json()['content']]


def private_feed(token, user_id):
    user_response = requests.get(app.config['USERS_API_URI'] + '/follow', headers={'Authorization': token})
    following = user_response.json()['following']
    feed = []
    for id in following:
        video_response = requests.get(app.config['VIDEOS_API_URI'] + '/videos/list/{}'.format(id))
        feed.append(video_response.json()['content'])
    feed.sort(reverse=True, key=lambda x: x['created_on'])
    return feed


# views
@app.route(route + '/feed', methods=['GET'])
def feed():
    if 'Authorization' not in request.headers.keys():
        feed = public_feed()
    else:
        token = request.headers.get('Authorization')
        user_id = request.get(app.config['USERS_API_URI'] + '/user/check', headers={'Authorization': token})
        feed = private_feed(token, user_id)
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
    return make_response(out)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
