from datetime import datetime
from typing import Dict
from apps.models.app_model import AppModel,model_metadata
from apps.models.origin import DataOrigin,load_origins
from apps.configs import configuration as conf
from apps.configs.vars import Vars

class DruidConnection(AppModel):
    def __init__(self,ip:str=conf.get(Vars.DRUID_HOST),port:int=conf.get(Vars.DRUID_PORT)):
        self.ip = ip
        self.port = port
        super().__init__()


@model_metadata({"connection":DruidConnection,"origin":DataOrigin})
class DruidCreateRequest(AppModel):
    def __init__(self, create_data:Dict):
        self.timestamp_col = create_data['timestamp_col']
        self.datasource = create_data['datasource']
        self.base_path = create_data.get('base_path','/tmp')
        self.connection = create_data.get("connection",DruidConnection())
        self.metrics = create_data.get('metrics',[ {"type": "count","name": "count"}])
        self.ignore_failed = create_data.get('ignore_failed',False)
        self.query_granularity = create_data.get('query_granularity','none')
        self.segment_granularity = create_data.get('segment_granularity','day')
        self.origin = create_data["origin"]

@model_metadata({})
class DruidBulkCreateRequest(AppModel):
    def __init__(self, create_data:Dict):
        self.requests=[]

        origins = []

        for o in create_data["origins"]:
            origins=origins+load_origins(o)

        for origin in origins:
            create_data["origin"]=origin
            create_request = DruidCreateRequest.from_dict(create_data)
            self.requests.append(create_request)
