import os
import json
from wsgiref.simple_server import make_server

from webframework.webframework import WebFramework, Response


TEMPLATE_DIR = '{}/templates/'.format(os.getcwd())

app = WebFramework()


@app.route('^/$')
def home(request):
    return Response(body='Home'.encode())


@app.route('^/comment/?$')
def comment(request):
    template = 'comment.html'

    if request.method == 'POST':
        print(request.POST)
        redirect = Response(status="302 Found")
        redirect.headers["Location"] = "/"
        return

    with open('{}{}'.format(TEMPLATE_DIR, template)) as f:
        html = f.read()
    return Response(body=html.encode())


@app.route('^/api/get/regions/?$')
def get_regions(request):
    query = 'SELECT id, name FROM regions WHERE deleted=0'
    regions = app.sql(query)
    body = json.dumps(dict(regions), ensure_ascii=False)
    response = Response(body=body.encode())
    response.headers['Content-Type'] = 'application/json'
    return response
    #return Response(body=body.encode(), content_type='application/json')


@app.route('^/api/get/cities/byregion/([0-9]+)/?$')
def get_cities_by_region(request):
    region_id = request.params[0]
    query = 'SELECT id, name FROM cities WHERE region_id=? AND deleted=0'
    params = (region_id,)
    cities = app.sql(query, params)
    body = json.dumps(dict(cities), ensure_ascii=False)
    response = Response(body=body.encode())
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, app)
        print('Serving on port 8000...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
