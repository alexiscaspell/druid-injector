from apps.models.druid import DruidBulkCreateRequest,DruidCreateRequest
from typing import List,Dict
from apps.services import druid_service
from apps.utils.logger_util import get_logger
from apps.utils.redis import redis_manager
from threading import Thread

logger=get_logger(__name__)

STATUS_LISTS = "DRUID_TASKS_STATUS"

def process(bulk_create:DruidBulkCreateRequest)->Dict:

    thread = Thread(target = _process, args = (bulk_create, ))
    thread.start()

    return {}

def _process(bulk_create:DruidBulkCreateRequest):

    for create_request in bulk_create.requests:
        try:
            druid_service.update_datasource(create_request)
            _add_to_success(create_request)
        except Exception as e:
            logger.error(e)
            _add_to_failed(create_request)

def _add_to_success(create_request:DruidCreateRequest):
    result = {"origin":create_request.origin.metadata,"success":True}

    redis_manager.push(STATUS_LISTS,result)

def _add_to_failed(create_request:DruidCreateRequest):
    result = {"origin":create_request.origin.metadata,"success":False}

    redis_manager.push(STATUS_LISTS,result)

def get_status():
    return redis_manager.get_list_items(STATUS_LISTS)

def refresh():
    redis_manager.clear(STATUS_LISTS)