import multiprocessing
from constants import WEIRD_PH

def serialize_json(json_string):
    """
        Due to Redis do not support json, we make a hack
    """
    return json_string.replace("\"", WEIRD_PH)

def deserialize_json(serialized_json_string):
    """
        Due to Redis do not support json, we make a hack
    """
    return serialized_json_string.replace(WEIRD_PH, "\"")

def create_pool_of_processes(_class, amount, *kwargs):
    processes = []
    for i in range(amount):
        p = multiprocessing.Process(target=_class, args=(str(i), *kwargs,))
        processes.append(p)
        p.start()
    return processes

def wait_for_pool(processes):
    for p in processes:
        p.join()

def naive_serialize(*kwargs):
    return "*-*".join(kwargs)

def naive_deserialize(naive_serialized_string):
    return naive_serialized_string.split("*-*")


