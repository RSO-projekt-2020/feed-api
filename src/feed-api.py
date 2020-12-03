from flask import *
from flask_sqlalchemy import SQLAlchemy
import datetime
from os import environ
import requests

route = '/v1'
app = Flask(__name__)
app.config['USERS_API_URI'] = 'http://users-api:8080/v1' # environ['USERS_API_URI'] 
app.config['VIDEOS_API_URI'] = 'http://videos-api:8080/v1' # environ['VIDEOS_API_URI']


# models
class Video(db.Model):
    __tablename__ = 'videos'

    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String)
    description = db.Column(db.String)
    width = db.Column(db.String)
    height = db.Column(db.String)
    created_on = db.Column(db.String)
    path = db.Column(db.String)

    def __init__(self, title, description, w, h, ts, path):
        self.title = title
        self.description = description
        self.width = w
        self.height = h
        self.created_on = str(datetime.datetime.utcnow())
        self.path = path

    def to_dict(self):
        tmp = {'title': self.title,
               'description': self.description,
               'width': self.width,
               'height': self.height,
               'created_on': self.created_on}
        return tmp


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
    if request.headers['Authorization'] is None:
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
            "mikrostoritve": [app.config['USERS_API_URI'] + "/v1/users/1", app.config['VIDEOS_API_URI'] + "/v1//videos/list"],
            "github": ["https://github.com/RSO-projekt-2020/users-api", "https://github.com/RSO-projekt-2020/videos-api", "https://github.com/RSO-projekt-2020/feed-api"],
            "travis": ["https://github.com/RSO-projekt-2020/users-api/actions", "https://github.com/RSO-projekt-2020/videos-api/actions", "https://github.com/RSO-projekt-2020/feed-api/actions"],
            "dockerhub": ["https://hub.docker.com/r/klemenstanic/users-api", "https://hub.docker.com/r/klemenstanic/video-api", "https://hub.docker.com/r/klemenstanic/feed-api"],
        }
    return make_response(out)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)