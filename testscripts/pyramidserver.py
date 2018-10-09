from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator

@view_config(route_name='theroute', renderer='json',request_method='POST')
def myview(request):
    import pdb; pdb.set_trace()
    return {'POST':''}

if __name__ == '__main__':
    config = Configurator()
    config.add_route('theroute', '/')
    config.scan()
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    print(server.base_environ)
    server.serve_forever()