"""

:file: tornado-sqlalchemy/models.py
:author: husobee
:date: 2014-05-13
:license: MIT License, 2014

    Models for the tornado application
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from tornado.concurrent import return_future, run_on_executor
from tornado.ioloop import IOLoop
from tornado.options import options
from concurrent.futures import ThreadPoolExecutor
import json

Base = declarative_base() # declaritive base for sqlalchemy

EXECUTOR = ThreadPoolExecutor(options.executor_max_threads) # setup global executor

class AnOrm(Base):
    """ Sqlalchemy ORM, mapping ot table an_orm """
    __tablename__ = 'an_orm'

    id = Column(Integer, primary_key=True) # has an int id
    name = Column(String) # has a name
    description = Column(String) # has a description

    def to_json(self): # hrm, serializing to_json
        return(json.dumps({ 'name': self.name, 'description':self.description })) #indeed

class AnOrmAsyncModel(object): # this model will manipulate the AnOrm instances
    def __init__(self, db_session, io_loop=None, executor=EXECUTOR): # initial setup as an executor
        self.io_loop = io_loop or IOLoop.instance() # grabe the ioloop or the global instance
        self.executor = executor # grab the executor
        self.db_session = db_session # get the session

    @run_on_executor # okay, run this method on the instance's executor
    @return_future # return a future
    def get_by_id(self, id:int, callback=None):
        """ AnOrmAsyncModel.get_by_id - Get AnOrm based on the ID from database """
        session = self.db_session() # setup the session in this thread
        result = None
        try:
            result = session.query(AnOrm).filter(AnOrm.id==id).one() # do the request
        except Exception as e:
            result = e
        session.close() # close the session
        callback(result) # return results by calling callback

    @run_on_executor # run this method on the instance's executor
    @return_future # return a future
    def create(self, an_orm, callback=None):
        """ AnOrmAsyncModel.create - Create an orm in the database """
        session = self.db_session() # setup session in this thread
        success = True
        try:
            session.add(an_orm) # add the orm to session
            session.commit() # commit the session when added
        except Exception as e: # if there was an exception
            session.rollback() # roll this back
            success = e # return that it failed
        session.close() # close the session
        callback(success) # return if it was success or not
