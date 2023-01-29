from apps.models.druid import DruidCreateRequest
from apps.utils.logger_util import get_logger
from typing import List,Dict
from datetime import datetime, timedelta
from os import getpid, makedirs, path
import requests
from apps.services import origin_service
import json


logger = get_logger(__name__)

class DruidTaskException(Exception):
    def __init__(self,*args,**kwargs):
        super().__init__(*args)

def load_info(cr:DruidCreateRequest)->List[Dict]:
    return origin_service.get_info(cr.origin)

def converter(o):
    if isinstance(o, datetime.datetime):
        return o.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(o, datetime.date):
        return o.strftime("%Y-%m-%d")
    else:
        try:
            return dict(o)
        except Exception as _:
            return str(o)


def cast_datetimes_to_iso_format(info: 'List[Dict]',create_request:'DruidCreateRequest'):
    for row in info:
        row[create_request.timestamp_col] = date_value(row[create_request.timestamp_col]).isoformat()

def cast_to_datetime(value):
    converted_value = None
    possible_formats = ["%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%S","%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f",
                        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", '%Y-%m-%d %H:%M:%S', "%Y-%m-%dT%H:%M:%SZ"]

    for possible_format in possible_formats:
        try:
            converted_value = datetime.strptime(
                str(value).lstrip().rstrip(), possible_format)
            return converted_value
        except BaseException as e:
            continue

    raise RuntimeError(f"No es posible castear {value} a datetime")

def date_value(date):
    if isinstance(date,datetime):
        return date

    # return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return cast_to_datetime(date)

def update_datasource(create_request:DruidCreateRequest):
    base_path = create_request.base_path+"/"

    druid_file_filename = 'cached' + str(datetime.now()) + '.json'
    druid_task_filename = 'cached' + str(datetime.now()) + '-task.json'

    druid_file = base_path + druid_file_filename

    logger.info('Saving druid injection file to: ' + druid_file)

    info_to_inject = load_info(create_request)

    cast_datetimes_to_iso_format(info_to_inject,create_request)

    info_to_inject.sort(key=lambda e: e[create_request.timestamp_col])

    with open(druid_file, 'w') as output:
        for l in info_to_inject:
            output.write(json.dumps(l, default=converter) + '\n')

    task = generate_druid_task(info_to_inject, create_request, base_path, druid_file_filename)
    
    r = requests.post(str(create_request.connection.ip) + ":" + str(create_request.connection.port)
                      + "/druid/indexer/v1/task", json=task,headers={"Content-Type": "application/json"})
    logger.info('Druid task output: ' + r.text)

    if "error" in json.loads(r.text):
        raise DruidTaskException(r.text)

    base_path = base_path+'druid_tasks/'
    if not path.exists(base_path):
        makedirs(base_path)
    save_task_filename = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    save_task_filename += druid_task_filename
    logger.info('Saving druid task to disk in: ' +
                base_path + save_task_filename)
    with open(base_path + save_task_filename, 'w') as output:
        json.dump(task, output,default=converter)

def _generate_fields(info:List[Dict], ts_field: str):
    ''' Esta funcion genera los campos para las dimensiones de druid'''
    gt_fields = info[0]
    some_list = []
    for field in gt_fields:
        value = gt_fields[field]

        if field == ts_field:
            continue
        if isinstance(value,str):
            some_list.append(field)
        elif isinstance(value,int):
            some_list.append({"name": field, "type": "long"})
        elif isinstance(value,float):
            some_list.append({"name": field, "type": "float"})
        else:
            raise AttributeError(
                "Field type does not match with the available field types. Field type:" +str(type(value)))
    return some_list

def generate_druid_task(info: List[Dict], create_request: DruidCreateRequest, base_dir: str, filename: str):

    values = info
    
    interval_min = date_value(values[0][create_request.timestamp_col])
    interval_min -= timedelta(days=1)
    interval_max = date_value(values[-1][create_request.timestamp_col])
    interval_max += timedelta(days=1)

    return {
        "type": "index",
        "spec": {
            "ioConfig" : {
                "type" : "index",
                "firehose" : {
                    "type" : "local",
                    "baseDir" : base_dir,
                    "filter" : filename
                },
                "appendToExisting" : False
            },

            "dataSchema": {
                    "dataSource": create_request.datasource,
                    "granularitySpec": {
                        "type": "uniform",
                        "segmentGranularity": str(create_request.segment_granularity),
                        "queryGranularity": str(create_request.query_granularity),
                        "intervals": [interval_min.strftime("%Y-%m-%d") + "/" + interval_max.strftime("%Y-%m-%d")],
                        "rollup":True
                    },
                    "parser": {
                        "type": "string",
                        "parseSpec": {
                            "format": "json",
                            "dimensionsSpec": {
                                "dimensions": _generate_fields(info, str(create_request.timestamp_col))
                            },
                            "timestampSpec": {
                                "format": "iso",
                                "column": create_request.timestamp_col
                            }
                        }
                    },
                    "metricsSpec": create_request.metrics},
            "tuningConfig": {
                "type" : "index",
                "maxRowsPerSegment" : 8000000,
                "maxRowsInMemory" : 40000,
                "ignoreInvalidRows":create_request.ignore_failed
                }
        }
    }
