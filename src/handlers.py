"""

:file: tornado-sqlalchemy/handlers.py
:author: husobee
:date: 2014-05-13
:license: MIT License, 2014

    Handlers for the tornado application

"""

from tornado import web, gen
from sqlalchemy.orm.exc import NoResultFound
from models import AnOrmAsyncModel, AnOrm
import json

class MainHandler(web.RequestHandler):
    """ MainHandler - Handle the root url, implemented post and get"""

    def initialize(self, db_session):
        """ MainHandler.initialize - Setup the Models we will need for this handler """
        self.an_orm_model = AnOrmAsyncModel(db_session)

    @web.asynchronous # this will be async
    @gen.coroutine # we will be using coroutines, with gen.Task
    def get(self, id):
        """ MainHandler.get - GET http method """
        value = yield gen.Task(self.an_orm_model.get_by_id, int(id)) # take the id, int it, and get by id from model
        try: 
            if isinstance(value.result(), Exception): # okay, future turned out to be an exception
                raise value.result() # raise it
        except NoResultFound as nrf: # is it a no results found exception?
            self.set_status(404) # then 404
            self.write("Not Found")
        except Exception as e: # uncaught other exception
            self.set_status(500) # we failed
            self.write("Internal Server Error")
        else: # no exception
            if isinstance(value.result(), AnOrm): # is it the thing we expected back?
                self.set_status(200) # good!
                self.write(value.result().to_json()) # return it
            else:
                self.set_status(500) # oh shit.
                self.write("Internal Server Error")
        self.finish() # finish the async response

    @web.asynchronous # this will be async
    @gen.coroutine # we will be using coroutine, with gen.Task
    def post(self, id):
        """ MainHandler.post - POST http method """
        posted_data = json.loads(self.request.body.decode('utf-8')) # get the body from the request
        value = AnOrm(name=posted_data.get('name'), description=posted_data.get('description')) # populate an ORM with it
        done = yield gen.Task(self.an_orm_model.create, value) # do the create, wait for it to finish
        try:
            if isinstance(done.result(), Exception): # check if exception
                raise done.result() # raise it
        except Exception as e: #catch all
            self.set_status(500) # write internal server fail
            self.write("Internal Server Error")
        else: # no exception
            if isinstance(done.result(), bool): # check if the result is the correct type
                self.set_status(200) # yay!
                self.write(json.dumps(done.result())) #write the response
            else: 
                self.set_status(500) # oh shit.
                self.write("Internal Server Error")
        self.finish() # finish the async response
