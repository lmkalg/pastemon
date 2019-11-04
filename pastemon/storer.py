import os
import os.path
import shutil
import redis

from auxiliaries import naive_deserialize
from logger import logger
from constants import ACTION_STORER_DELETE, ACTION_STORER_STORE, STORER_QUEUE, METADATA_SUFFIX

class Storer:
    """
        Class aimed to manipualte the storage of files
    """
    def __init__(self, _id, output_dir_path):
        self.redis_conn = redis.Redis()
        self._id = str(os.getpid())
        self.output_dir_path = output_dir_path
        self.work()
        
    def _store_file_as_interesting_file(self, path_to_file, name_matched_condition):
        """
            This function will save this file in a different directory
        """
        output_dir_path = os.path.join(self.output_dir_path, name_matched_condition)

        file_name = path_to_file.split('/')[-1]
        dst_file = os.path.join(output_dir_path, file_name)
        shutil.copy(path_to_file, dst_file)
        logger.log("<{}> Saving file {} as interesting one in {} dir".format(self.__class__.__name__ + self._id, file_name, name_matched_condition))

        path_to_file_metadata = path_to_file + METADATA_SUFFIX
        file_name_metadata = file_name + METADATA_SUFFIX
        dst_file_metadata = os.path.join(output_dir_path, file_name_metadata)
        shutil.copy(path_to_file_metadata, dst_file_metadata)
    
    def _delete_file_from_temporary_dir(self, path_to_file):
        """
            Once analyzed, remove it.
        """
        path_to_file_metadata = path_to_file + METADATA_SUFFIX
        logger.log("<{}> Deleting file {} and {}".format(self.__class__.__name__ + self._id, path_to_file, path_to_file_metadata))
        os.remove(path_to_file)
        os.remove(path_to_file_metadata)

    def work(self):
        while True:
            queue_name, data = self.redis_conn.blpop(STORER_QUEUE)
            path_to_file, condition_name, action = naive_deserialize(data.decode("utf-8"))
            if action == ACTION_STORER_DELETE:
                self._delete_file_from_temporary_dir(path_to_file)
            elif action == ACTION_STORER_STORE:
                self._store_file_as_interesting_file(path_to_file, condition_name)
            else:
                logger.warning("<{}> Received unknown action: {}. Just ignoring it. This could mean that no file was either stored or deleted".format(self.__class__.__name__ + self._id, action))