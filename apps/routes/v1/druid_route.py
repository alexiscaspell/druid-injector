from http import HTTPStatus

from flask import Blueprint, jsonify, request
from apps.utils.rest_util import get_valid_rest_object
from apps.utils.logger_util import get_logger

import apps.configs.configuration as conf
from apps.configs.vars import Vars
import apps.services.druid_service as druid_service
from apps.services import supervisor_service
from apps.models.druid import DruidCreateRequest,DruidBulkCreateRequest

URI = "/druid/injector"
VERSION = "/v1"

logger = get_logger(__name__)

blue_print = Blueprint(URI,
                       __name__,
                       url_prefix=conf.get(Vars.API_BASE_PATH)+VERSION+URI)


@blue_print.route('', methods=['POST'])
def update_datasource():
    create_request = DruidCreateRequest.from_dict(request.get_json(force=True))

    druid_service.update_datasource(create_request)

    return get_valid_rest_object({}),HTTPStatus.CREATED

@blue_print.route('/bulk', methods=['POST'])
def update_datasource_bulk():

    bulk_create = DruidBulkCreateRequest.from_dict(request.get_json(force=True))

    response = supervisor_service.process(bulk_create)

    return jsonify(response),HTTPStatus.OK

@blue_print.route('/bulk', methods=['GET'])
def get_bulk_status():

    response = supervisor_service.get_status()

    return jsonify(response),HTTPStatus.OK

@blue_print.route('/bulk/refresh', methods=['GET'])
def refresh_bulk_status():

    supervisor_service.refresh()

    return jsonify({}),HTTPStatus.OK
