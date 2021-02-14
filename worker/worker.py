import requests
import datetime
from tqdm import tqdm
from google.cloud import datastore
import os
from icecream import ic


class QiitaWorker(object):

    def __init__(self):

        self.access_token = os.environ.get('QIITA_TOKEN')

        self.base_url = "https://qiita.com/api/v2/"
        self.items_url = self.base_url + "users/sasayabaku/items?per_page=100"
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

        task['date'] = datetime.datetime.now()

        task['likes'] = self.total['likes']
        task['views'] = self.total['views']
        task['stocks'] = self.total['stocks']

        self.datastore_client.put(task)

    def _get_item_stock(self, item):
        _url = self.items_url + str(item) + "/stockers"
        stock_json = requests.get(_url, headers=self.headers).json()
        return stock_json