# Flask imports
from flask import g, url_for
import flask_restful as restful
from flask_restful import marshal

# Flaskit imports
from celery.result import AsyncResult
from celery.exceptions import TimeoutError
from consumer_amazingresources import CONSUMER_APP
from pagination import get_paginated_list
from flaskit import app
from flaskit.utils import ErrorNotFound, ErrorDuplicate
from flaskit.resource import MetaResource, init_api, generate_swagger_from_schema
from celery.signals import after_task_publish

# Project imports

# Python imports
import sys
import copy
import json

#===================================
# AmazingresourcesTest swagger fields
#===================================

@generate_swagger_from_schema(schemaRef="AmazingresourcesTest", schemaPath="definitions/respon\
se", type="Response")
class AmazingresourcesTestResponseFields:
    pass



#=========================
# AmazingresourcesGet swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="AmazingresourcesGet", schemaPath="definitions/response/properties/results/items", type="Response")
class AmazingresourcesGetResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="AmazingresourcesGet", schemaPath="definitions/response", type="Response")
class AmazingresourcesGetResponseFields:
    pass

@generate_swagger_from_schema(schemaRef="AmazingresourcesStatus", schemaPath="definitions/response", type="Response")
class AmazingresourcesStatusResponseFields:
    pass



#=========================
# AmazingresourcesPost swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="AmazingresourcesPost", schemaPath="", type="Request")
class AmazingresourcesPostRequestFields:
    pass

@generate_swagger_from_schema(schemaRef="AmazingresourcesPost", schemaPath="definitions/response/properties/", type="Response")
class AmazingresourcesPostResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="AmazingresourcesPost", schemaPath="definitions/response", type="Response")
class AmazingresourcesPostResponseFields:
    pass

#=========================
# AmazingresourcesDelete swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="AmazingresourcesDelete", schemaPath="definitions/response/properties/amazingresources", type="Response")
class AmazingresourcesDeleteResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="AmazingresourcesDelete", schemaPath="definitions/response", type="Response")
class AmazingresourcesDeleteResponseFields:
    pass



##################################################################################################
# Test resource
##################################################################################################
class Test(MetaResource):
    """Manage test
    """
    @init_api("AmazingresourcesTest")
    def post(self):
        """Test check

        Run test task

        TITLE:Sample
        <pre>
        CURL:"/amazingresources/_test" -d '{"description": "..."}'
        </pre>
        """

        self.initializeAPI()

        kwargs = copy.deepcopy(g.args)
        kwargs.pop('async', None)
        kwargs.pop('range', None)
        async_result = CONSUMER_APP.send_task(
            'amazingresources.test', kwargs=kwargs, queue='amazingresources')

        if g.args['async']:
            headers = {
                'Location': url_for(
                    'amazingresourcesStatusById',
                    id=async_result.id,
                    _external=True),
                'Content-Location': url_for(
                    'amazingresourcesById',
                    id=async_result.id,
                    _external=True),
            }

            return {}, 202, headers
        resp = async_result.get()
        if not isinstance(resp['results'], list):
            resp['results'] = [resp['results']]
        return get_paginated_list(
            resp['results'], async_result.id,
            g.args['range'], 'amazingresourcesById')
##################################################################################################
# Amazingresources resource for post verbs
##################################################################################################
class Amazingresources(MetaResource):
    """Manage amazingresources
    """

    ####################################################################################
    # Create a amazingresources
    ####################################################################################
    @init_api("AmazingresourcesPost")
    def post(self):
        """Create a amazingresources

        TITLE:Sample
        <pre>
        CURL:"/amazingresources" -d '{"description": "..."}'
        </pre>
        """

        self.initializeAPI()

        if g.dryrun:
            AmazingresourcesRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return AmazingresourcesRecord, 200, {}

        kwargs = copy.deepcopy(g.args)
        kwargs.pop('range', None)
        kwargs.pop('async', None)
        async_result = CONSUMER_APP.send_task(
            'amazingresources.post', kwargs=kwargs, queue='amazingresources')

        if g.args['async']:
            headers = {
                'Location': url_for(
                    'amazingresourcesStatusById',
                    id=async_result.id,
                    _external=True),
                'Content-Location': url_for(
                    'amazingresourcesById',
                    id=async_result.id,
                    _external=True),
            }

            return {}, 202, headers
        else:
            resp = async_result.get()
            if not isinstance(resp['results'], list):
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'amazingresourcesById')


############################
# Qualified Amazingresources
############################
class AmazingresourcesById(MetaResource):
    """Manage qualified Amazingresources
    """
    ####################################################################################
    # Get a amazingresources
    ####################################################################################
    @init_api("AmazingresourcesGet")
    def get(self, id):
        """Get amazingresources

        Get amazingresources informations

        TITLE:Sample
        <pre>
        CURL:"/amazingresources/<id>"
        </pre>
        """

        # verify request
        self.initializeAPI(data = { "id": id })

        if g.dryrun:
            AmazingresourcesRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return AmazingresourcesRecord, 200

        kwargs = copy.deepcopy(g.args)
        async_result = AsyncResult(id, app=CONSUMER_APP)

        # Check if we are getting a resource or a task result. (A resource being
        # a task.get result)
        if async_result.state == 'SUCCESS':
            resp = async_result.get()
            if not resp.get('success', False):
                return resp.get('error_msg', 'Task failed'), 200
            if not resp.get('results', False):
                resp['results'] = []
            if not isinstance(resp['results'], list):
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'amazingresourcesById')

        return {}, 404


    ####################################################################################
    # Delete a amazingresources
    ####################################################################################
    @init_api("AmazingresourcesDelete")
    def delete(self, id):
        """Delete a task result

        TITLE:Sample
        <pre>
        CURL:"/amazingresources/<id>"
        </pre>
        """

        # verify request
        self.initializeAPI(data = { "id": id })
        task = AsyncResult(id, app=CONSUMER_APP)
        if task.state != 'SUCCESS':
            return 'Task result not found', 404
        task.forget()
        return '', 204




class AmazingresourcesStatusById(MetaResource):
    """Get Amazingresources status
    """
    ###############################
    # Get a amazingresources status
    ###############################
    @init_api("AmazingresourcesStatus")
    def get(self, id):
        """Get a amazingresources status

        TITLE:Sample
        <pre>
        CURL:"/amazingresources/<id>/status"
        </pre>
        """
        self.initializeAPI(data = { "id": id })

        async_res = AsyncResult(id, app=CONSUMER_APP)
        return {'state': async_res.state}, 200