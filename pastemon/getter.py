import os
import requests
import json
import time
import urllib3
import redis

from constants import PASTES_DATA_QUEUE, SECONDS_TO_WAIT
from auxiliaries import serialize_json
from logger import logger

urllib3.disable_warnings()

class Getter:

    def __init__(self, _id, time_to_wait, amount_of_pastes_to_fetch):
        self.amount_of_pastes_to_fetch = amount_of_pastes_to_fetch #(MAX!)
        self.redis_conn = redis.Redis()
        self._id = str(os.getpid())
        self.time_to_wait = time_to_wait

        self._get_new_pastes_data()

    def _get_new_pastes_data(self):
        """ 
            In charge of gathering new pastes each X minutes.
            Once it gets new data, it is pushed to a REDIS queue
        """
        
        uri = "https://scrape.pastebin.com/api_scraping.php?limit={}".format(
                    self.amount_of_pastes_to_fetch)
        
        cache = set()
        while True:
            new_pastes = 0
            logger.log("<{}> Going for new pastes".format(self.__class__.__name__ + self._id))
            r = requests.get(uri)
            logger.log("<{}> New pastes fetched!".format(self.__class__.__name__ + self._id))
            data = json.loads(r.text)
            for paste_data in data:
                key = paste_data["key"]
                if key not in cache:
                    new_pastes+=1
                    cache.add(key)
                    self.redis_conn.rpush(PASTES_DATA_QUEUE, serialize_json(json.dumps(paste_data)))

            logger.log("<{}> Found: {} new pastes!".format(self.__class__.__name__ + self._id, new_pastes))
            logger.log("<{}> Waiting {} seconds... ".format(self.__class__.__name__ + self._id, self.time_to_wait))
            time.sleep(self.time_to_wait)