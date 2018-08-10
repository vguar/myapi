# Flask imports
from flask import g
import flask_restful as restful
from flask_restful import marshal

# Flaskit imports
from flaskit import app
from flaskit.utils import ErrorNotFound
from flaskit.resource import MetaResource, init_api, generate_swagger_from_schema
from consumer_amazingresources import CONSUMER_APP

# Python imports
import sys
import copy
import json



#=========================
# health swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="HealthGet", schemaPath="definitions/response/properties/results/items", type="Response")
class HealthGetResponseResultsFields:
    pass

@generate_swagger_from_schema(schemaRef="HealthGet", schemaPath="definitions/response", type="Response")
class HealthGetResponseFields:
    pass


##################################################################################################
# Health resource
##################################################################################################
class Health(MetaResource):
    """Manage health
    """
    @init_api("HealthGet")
    def get(self):
        """Health check

        Run health check

        TITLE:Sample
        <pre>
        CURL:"/_health"
        </pre>
        """

        self.initializeAPI()

        resp = CONSUMER_APP.control.ping()

        return [list(worker.keys())[0] for worker in resp], 200