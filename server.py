import os
import json
from wsgiref.simple_server import make_server

from webframework.webframework import WebFramework, Response


TEMPLATE_DIR = '{}/templates/'.format(os.getcwd())

app = WebFramework()


@app.route('^/$')
def home(request):
    data = app.sql('select * from cities')
    print(data)
    return Response(body='Home'.encode())


@app.route('^/comment/')
def comment(request):
    template = 'comment.html'

    if request.method == 'POST':
        print(request.POST)

    with open('{}{}'.format(TEMPLATE_DIR, template)) as f:
        html = f.read()
    return Response(body=html.encode())


@app.route('^/api/get/regions/')
def get_regions(request):
    query = 'SELECT id, name FROM regions WHERE deleted=0'
    regions = app.sql(query)
    body = json.dumps(dict(regions), ensure_ascii=False)
    return Response(body=body.encode(), content_type='application/json')


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, app)
        print('Serving on port 8000...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
