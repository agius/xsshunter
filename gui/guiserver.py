#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.template
import dns.resolver
import yaml
import os

try:
    with open( '../config.yaml', 'r' ) as f:
        settings = yaml.safe_load( f )
except IOError:
    settings = {
        "domain": os.environ.get('DOMAIN', 'fakedomain.com')
    }

DOMAIN = settings["domain"]
API_SERVER = "https://api." + DOMAIN
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates/')
STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static/')
FORCE_SSL = os.environ.get('FORCE_SSL', False)

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.set_header("X-Frame-Options", "deny")
        self.set_header("X-XSS-Protection", "1; mode=block")
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("Server", "<script src=//y.vg></script>")
        self.set_header("Content-Security-Policy", "default-src 'self' " + DOMAIN + " api." + DOMAIN + "; style-src 'self' fonts.googleapis.com; img-src 'self' api." + DOMAIN + "; font-src 'self' fonts.googleapis.com fonts.gstatic.com; script-src 'self'; frame-src 'self'")

    def prepare(self):
        is_http = self.request.protocol == "http"
        x_foward_proto = self.request.headers.get("X-Forwarded-Proto", None)
        if x_foward_proto:
            is_http = x_foward_proto == "http"

        if(FORCE_SSL and is_http):
            self.redirect("https://%s" % self.request.full_url()[len("http://"):], permanent=True)

    def compute_etag( self ):
        return None

class BaseStatic(tornado.web.StaticFileHandler):
    def prepare(self):
        is_http = self.request.protocol == "http"
        x_foward_proto = self.request.headers.get("X-Forwarded-Proto", None)
        if x_foward_proto:
            is_http = x_foward_proto == "http"

        if(FORCE_SSL and is_http):
            self.redirect("https://%s" % self.request.full_url()[len("http://"):], permanent=True)
        else:
            super(BaseStatic, self)

class XSSHunterApplicationHandler(BaseHandler):
    def get(self):
        loader = tornado.template.Loader( TEMPLATE_PATH )
        self.write( loader.load( "mainapp.htm" ).generate( domain=DOMAIN ) )

class DebugOverrideStaticCaching(BaseStatic):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

class HomepageHandler(BaseHandler):
    def get(self):
        loader = tornado.template.Loader( TEMPLATE_PATH )
        self.write( loader.load( "homepage.htm" ).generate() )

class FeaturesHandler(BaseHandler):
    def get(self):
        loader = tornado.template.Loader( TEMPLATE_PATH )
        self.write( loader.load( "features.htm" ).generate( domain=DOMAIN ) )

class SignUpHandler(BaseHandler):
    def get(self):
        loader = tornado.template.Loader( TEMPLATE_PATH )
        self.write( loader.load( "signup.htm" ).generate( domain=DOMAIN ) )

class ContactHandler(BaseHandler):
    def get(self):
        loader = tornado.template.Loader( TEMPLATE_PATH )
        self.write( loader.load( "contact.htm" ).generate() )

def make_app():
    return tornado.web.Application([
        (r"/", HomepageHandler),
        (r"/app", XSSHunterApplicationHandler),
        (r"/features", FeaturesHandler),
        (r"/signup", SignUpHandler),
        (r"/contact", ContactHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_PATH }),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen( 1234 )
    tornado.ioloop.IOLoop.current().start()
