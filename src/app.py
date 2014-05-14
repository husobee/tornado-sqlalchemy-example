"""

:file: tornado-sqlalchemy/app.py
:author: husobee
:date: 2014-05-13
:license: MIT License, 2014

    Small example of using sqlalchemy with tornado, with an executor, to not block up ioloop

"""
from tornado.options import define, options, parse_command_line # tornado options related imports

define("port", default=8888, help="Port for webserver to run") # need the port to run on
define("db_connection_str", default="sqlite:///default.sqlite.db", help="Database connection string for application") # db connection string
define("executor_max_threads", default=20, help="max threads for threadpool executor") # max number of threads for executor

parse_command_line() # firstly, get the above options from command line

from tornado import ioloop, web
from handlers import MainHandler # this is our main handler

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base as models_base # get the declared sqlalchemy base

db_engine = create_engine(options.db_connection_str) # setup db engine for sqlalchemy
db_session = sessionmaker() # setup the session maker for sqlalchemy

class MyApplication(web.Application):
    """ Inhierited tornado.web.Application - stowing some sqlalchemy session information in the application """
    def __init__(self, *args, **kwargs):
        """ setup the session to engine linkage in the initialization """
        self.session = kwargs.pop('session')
        self.session.configure(bind=db_engine)
        super(MyApplication, self).__init__(*args, **kwargs)

    def create_database(self):
        """ this will create a database """
        models_base.metadata.create_all(db_engine)

application = MyApplication([ # here is our url/handler mappings
    (r"/([^/]*)", MainHandler, dict(db_session=db_session)), # main handler takes a url parm, and we are passing session to initialize
], session=db_session)

if __name__ == "__main__": # main
    application.create_database() # create the database
    application.listen(options.port) # listen on the right port
    ioloop.IOLoop.instance().start() # startup ioloop


