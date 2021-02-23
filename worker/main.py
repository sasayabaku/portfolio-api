from flask import Flask, jsonify
from flask_cors import CORS
import requests
import datetime
from tqdm import tqdm
from google.cloud import datastore
import os


class QiitaWorker(object):

    def __init__(self):

        self.access_token = os.environ.get('QIITA_TOKEN')

        _username = 'sasayabaku'

        self.base_url = "https://qiita.com/api/v2/"
        self.items_url = self.base_url + "users/" + _username + "/items?per_page=100"
        self.item_url = self.base_url + "items/"

        self.headers = {
            "content-type": "application/json",
            "Authorization": "Bearer " + self.access_token
        }

        self.total = {
            "likes": 0,
            "views": 0,
            "stocks": 0
        }

        self._get_post_list()

        self.datastore_client = datastore.Client()

    def _get_post_list(self):
        json = requests.get(self.items_url, headers=self.headers)
        self.items_list = [item['id'] for item in json.json()]

    def collect(self):
        for item in tqdm(self.items_list):
            _url = self.item_url + str(item)
            res_json = requests.get(_url, headers=self.headers).json()
            stock_json = self._get_item_stock(item)
            item_new_document = {
                "id": item,
                "likes": res_json['likes_count'],
                "views": res_json['page_views_count'],
                "stocks": len(stock_json)
            }

            self.total['likes'] += item_new_document['likes']
            self.total['views'] += item_new_document['views']
            self.total['stocks'] += item_new_document['stocks']

    def update_datastore(self):
        kind = "Aggregate"
        task_key = self.datastore_client.key(kind)

        task = datastore.Entity(key=task_key)

        task['date'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

        task['likes'] = self.total['likes']
        task['views'] = self.total['views']
        task['stocks'] = self.total['stocks']

        self.datastore_client.put(task)

    def _get_item_stock(self, item):
        _url = self.item_url + str(item) + "/stockers"
        stock_json = requests.get(_url, headers=self.headers).json()
        return stock_json


app = Flask(__name__)
CORS(app)

@app.route('/')
def worker():
    worker = QiitaWorker()
    worker.collect()
    worker.update_datastore()

    return jsonify({'message': 'work success'}), 200

@app.route('/hello')
def hello():
    return jsonify({'message': "Hello new world"})

@app.route('/get_work')
def get_work():

    datastore_client = datastore.Client()

    query = datastore_client.query(kind="Aggregate")
    datastore_response = query.fetch()
    data_list = list(datastore_response)

    data = list([])

    for item in data_list:
        _json = {
            "date": item['date'].isoformat(),
            "likes": int(item['likes']),
            "stocks": int(item['stocks']),
            "views": int(item['views'])
        }

        data.append(_json)

    data = sorted(data, key=lambda x: x['date'])

    return jsonify({"data": data}), 200


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
