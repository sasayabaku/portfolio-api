from .worker import QiitaWorker
from icecream import ic

"""Qiita Logger main script

This script works below

1. Collect total views / likes / stocks from Qiita API
2. Sum each value
3. Upload to FireStore
"""

worker = QiitaWorker()

worker.collect()

ic(worker.total)

worker.update_datastore()