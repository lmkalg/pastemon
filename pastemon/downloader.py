import time
import requests
import redis
import json
import os.path
import codecs

from auxiliaries import deserialize_json
from constants import PD_KEY, PASTES_DATA_QUEUE, PASTES_TO_ANALIZE_QUEUE, METADATA_SUFFIX
from logger import logger

class Downloader:
    def __init__(self, _id, analysis_dir_path):
        self.redis_conn = redis.Redis()
        self.uri_download_raw_content = "https://scrape.pastebin.com/api_scrape_item.php?i={}"
        self._id = str(os.getpid())
        self.analysis_dir_path = analysis_dir_path
        
        self._download_pastes()

    def _get_paste_data_from_redis(self):
        """ 
            Gets the data from the Redis queue
        """
        queue_name, paste_data = self.redis_conn.blpop(PASTES_DATA_QUEUE)
        return json.loads(deserialize_json(paste_data.decode(encoding="utf-8"))) 
        
    def _download_content_of_paste(self, paste_data):
        """
            Gets the RAW data of the paste using the unique key
        """
        key = paste_data[PD_KEY]
        attempts = 0
        logger.log("<{}> Downloading content of paste {}".format(self.__class__.__name__ + self._id, key))
        while attempts < 20:
            try:
                r = requests.get(self.uri_download_raw_content.format(key))
                if r.status_code == 200:
                    return r.text
                else:
                    raise Exception("Error while trying to get the paste with key: {}. HTTP code {}.\n HTTP error message: {}".format(key, r.status_code, r.text))
            except requests.exceptions.ConnectionError as e:
                logger.log("<{}> Exception trying to get resource: {}.\n Exception: {}\n".format(self.__class__.__name__ + self._id, self.uri_download_raw_content(key), str(e)))
                time.sleep(30)
                attempts +=1


    def _write_file_and_push_data_to_redis(self, paste_content, paste_data):
        """
            Writes down the actual content of the paste. Also, pushes the path 
            of this file to a redis in push so the analyzers know where to search
            for these kind of files.
        """ 
        key = paste_data[PD_KEY]
        logger.log("<{}> Writing file and uploading data of paste {}".format(self.__class__.__name__ + self._id, key))
        path_to_file = os.path.join(self.analysis_dir_path, key)
        with codecs.open(path_to_file, 'w', 'utf-8') as f:
            f.write(paste_content)
        path_to_file_metadata = path_to_file + METADATA_SUFFIX
        with codecs.open(path_to_file_metadata, 'w', 'utf-8') as g:
            g.write(str(paste_data))
        self.redis_conn.rpush(PASTES_TO_ANALIZE_QUEUE, path_to_file)

    def _download_pastes(self):
        """
            This method gets the data from the Redis queue, goes
            for the actual content of the paste by using the pastebin
            API, and stores the content of the paste in the filesystem.
        """
        while True:
            paste_data = self._get_paste_data_from_redis()
            content = self._download_content_of_paste(paste_data)
            self._write_file_and_push_data_to_redis(content, paste_data)