#!/usr/bin/env python

import os
import sys
import logging

import tornado.template
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.routing

from api import apiserver
from gui import guiserver

DOMAIN = os.environ.get('DOMAIN', '127.0.0.1')
API_DOMAIN = "api." + DOMAIN

API_APP = apiserver.make_app()
GUI_APP = guiserver.make_app()

def init_logger(log):
    log.propagate = False
    stdout_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stdout_handler)

def make_app():
    return tornado.web.Application([
        tornado.routing.Rule(tornado.routing.HostMatches("www." + DOMAIN), GUI_APP),
        tornado.routing.Rule(tornado.routing.HostMatches(DOMAIN), GUI_APP),
        tornado.routing.Rule(tornado.routing.AnyMatches(), API_APP)
    ])

if __name__ == "__main__":
    args = sys.argv
    tornado.options.parse_command_line(args)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    init_logger(logging.getLogger('tornado.access'))
    init_logger(logging.getLogger('tornado.application'))
    init_logger(logging.getLogger('tornado.general'))
    apiserver.create_all()
    app = make_app()
    app.listen( os.environ.get('PORT', 8080) )
    tornado.ioloop.IOLoop.current().start()
