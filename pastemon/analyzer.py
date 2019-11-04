import redis
import yaml
import re
import os
import codecs

from auxiliaries import naive_serialize
from constants import PASTES_TO_ANALIZE_QUEUE, METADATA_SUFFIX, STRING, REGEX, NAME, STORER_QUEUE, ACTION_STORER_STORE, ACTION_STORER_DELETE
from logger import logger
from condition import RegexCondition, StringCondition

class Analyzer:
    """
        Paste in charge of analyzing the content of each paste
        to understand if there could be some password there
    """
    def __init__(self, _id, conditions_file):
        self.redis_conn = redis.Redis()
        self._id = str(os.getpid())
       
        self._generate_conditions_from_file(conditions_file)
        self._analyze_pastes_contents()

    def _generate_conditions_from_file(self, conditions_file):
        """
            Parse the YAML conditions file to generate the matching conditions
        """
        self.conditions = []
        with open(conditions_file) as f:
            content = yaml.safe_load(f)
        
        for condition_name, condition_properties in content.items():
            condition_properties.update({NAME:condition_name})
            if STRING in condition_properties:
                self.conditions.append(StringCondition(**condition_properties))
            elif REGEX in condition_properties:
                self.conditions.append(RegexCondition(**condition_properties))
            else:
                raise Exception("Badformed condition named {}. Neither '{}' nor '{}' keywords are present.".format(condition_name, STRING, REGEX))

    def _restart_conditions(self):
        """
            Restarts all conditions
        """
        for condition in self.conditions:
            condition.restart()

    def _get_paste_content(self):
        """ 
            Gets the path to the file from the Redis queue.
            Afterwards, read the file content
        """
        queue_name, path_to_file = self.redis_conn.blpop(PASTES_TO_ANALIZE_QUEUE)
        path_to_file  = path_to_file.decode('utf-8')
        with codecs.open(path_to_file, 'r', "utf-8") as f:
            content = f.read()
        return content, path_to_file

    def _match_conditions(self, content):
        """
            If it matches some of the conditions provided, then is because we believe it could be 
            somehow an interesting paste

            Return the names of the conditions that matched
        """
        matched_conditions_names = []
        for line in content.split('\n'):
            for condition in self.conditions:
                # If all of them matched, there is no need to continue.
                if len(matched_conditions_names) == len(self.conditions):
                    return matched_conditions_names
                else:
                    if condition.match(line):
                        matched_conditions_names.append(condition.condition_name())
        return matched_conditions_names

    def _analyze_pastes_contents(self):
        """ 
            Gets the path to the files that need to be parsed and then afterwards 
            executes all the regex to understand if there is some matching. 
            If there is a match, it saves the file in another place. If there isn't 
            it just deletes the file.
        """
        while True:
            content, path_to_file = self._get_paste_content()
            logger.log("<{}> Analyzing file: {}".format(self.__class__.__name__ + self._id, path_to_file))
            
            matched_conditions_names = self._match_conditions(content)
            if matched_conditions_names:
                for condition_name in matched_conditions_names:
                    logger.log("<{}> Condition {} matched for file {}".format(self.__class__.__name__ + self._id, condition_name, path_to_file))
                    self.redis_conn.rpush(STORER_QUEUE, naive_serialize(path_to_file, condition_name, ACTION_STORER_STORE))

            self.redis_conn.rpush(STORER_QUEUE, naive_serialize(path_to_file, "", ACTION_STORER_DELETE))
            self._restart_conditions()