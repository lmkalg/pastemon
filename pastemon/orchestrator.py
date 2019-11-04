import multiprocessing
import yaml
import os
import os.path

from getter import Getter
from downloader import Downloader
from analyzer import Analyzer
from storer import Storer
from condition import RegexCondition, StringCondition
from logger import logger
from auxiliaries import create_pool_of_processes, wait_for_pool
from constants import STRING, REGEX

class Orchestrator:
    def __init__(self, downloaders, getters, analyzers, storers, analysis_dir_path, output_dir_path, conditions_file_path, time_to_wait, amount_of_pastes_to_fetch):
        self.amount_of_downloaders = downloaders
        self.amount_of_getters = getters
        self.amount_of_analyzers = analyzers
        self.amount_of_storers = storers
        self.analysis_dir_path = analysis_dir_path
        self.output_dir_path = output_dir_path
        self.conditions_file_path = conditions_file_path
        self.time_to_wait = time_to_wait
        self.amount_of_pastes_to_fetch = amount_of_pastes_to_fetch

        self._validate_conditions_file()
        self._create_analysis_dir()

    def _create_analysis_dir(self):
        """
            Function just to create the analysis dir if not present.
        """
        os.makedirs(self.analysis_dir_path, exist_ok=True)
        

    def _validate_conditions_file(self):
        """
            Function that attempts to validate the YAML
            to be sure that nothing is misswritten.
        """
        # Try to parse the YAML, otherwise leave the exception
        with open(self.conditions_file_path) as f:
            content = yaml.safe_load(f)

        # Try to create Conditions, otherwise leave the exception
        for condition_name, condition_properties in content.items():
            if STRING in condition_properties:
                StringCondition(**condition_properties)
            elif REGEX in condition_properties:
                RegexCondition(**condition_properties)
            else:
                raise Exception("Badformed condition named {}. Neither '{}' nor '{}' keywords are present.".format(condition_name, STRING, REGEX))

        
        # Once it seems that everything is ok, create the output dirs for each condition
        for condition_name, condition_properties in content.items():
            full_condition_path = os.path.join(self.output_dir_path, condition_name)
            os.makedirs(full_condition_path, exist_ok=True)

    def big_bang(self):
        """
            Start the whole framework
        """
        getters = create_pool_of_processes(Getter, self.amount_of_getters, self.time_to_wait, self.amount_of_pastes_to_fetch)
        downloaders = create_pool_of_processes(Downloader, self.amount_of_downloaders, self.analysis_dir_path)
        analyzers = create_pool_of_processes(Analyzer, self.amount_of_analyzers, self.conditions_file_path)
        storers = create_pool_of_processes(Storer, self.amount_of_storers, self.output_dir_path)

        wait_for_pool(getters)
        wait_for_pool(downloaders)
        wait_for_pool(analyzers)
        wait_for_pool(storers)

