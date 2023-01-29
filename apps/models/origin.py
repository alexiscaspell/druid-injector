from datetime import datetime
from typing import Dict,List
from apps.models.app_model import AppModel,model_metadata
from apps.configs import configuration as conf
from apps.configs.vars import Vars
from enum import Enum
import os
from copy import deepcopy
import glob
from apps.utils.logger_util import get_logger

logger = get_logger(__name__)

class DataOriginType(Enum):
    csv = "csv"
    json = "json"
    b64 = "b64"
    redis = "redis"

@model_metadata({"type":DataOriginType})
class DataOrigin(AppModel):
    def __init__(self,origin_dict:Dict):
        self.type = origin_dict["type"]
        self.metadata = origin_dict["metadata"]
        self.bulk = origin_dict.get("bulk",False)

def load_origins(origin_dict:Dict)->List[Dict]:


    origin = DataOrigin.from_dict(origin_dict)

    logger.debug(f"BULK: {origin.bulk}")

    if not origin.bulk:
        return [origin_dict]

    regex = origin.metadata["path"]

    matched = glob.glob(regex)

    logger.debug(f"ENCONTRADOS {matched} como origenes")

    origin_dicts = []

    for entry in matched:
        new_origin_dict = deepcopy(origin_dict)
        new_origin_dict["metadata"]["path"]=entry

        origin_dicts.append(new_origin_dict)

    return origin_dicts

