from wsgiref.simple_server import make_server

from webframework.webframework import WebFramework, Response


app = WebFramework()


@app.route("^/$")
def home(request):
    data = app.db_read('select * from cities')
    print(data)
    return Response(body="Home".encode())


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, app)
        print('Serving on port 8000...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
