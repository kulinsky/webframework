import os
import json
import datetime
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
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        middlename = request.POST.get('middlename', None)
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        comment_text = request.POST.get('subject', None)

        try:
            city_id = int(request.POST.get('city_id'))
        except TypeError:
            city_id = -1

        query = (
            "INSERT INTO users(last_name, first_name, middle_name," +
            " phone, email, city_id) VALUES(?,?,?,?,?,?)"
        )

        params = (lastname, firstname, middlename, phone, email, city_id)
        print(params)
        app.sql(query, params)

        user_id = app.sql('SELECT * FROM users ORDER BY id DESC LIMIT 1;')[1][0][0]

        now = datetime.datetime.now()
        query = 'INSERT INTO comments(text, user_id, timestamp) VALUES(?,?,?);'
        params = (comment_text, user_id, now)
        app.sql(query, params)

        redirect = Response(status="302 Found")
        redirect.headers["Location"] = "/view/"
        return redirect

    with open('{}{}'.format(TEMPLATE_DIR, template)) as f:
        html = f.read()
    return Response(body=html.encode())


@app.route('^/view/?$')
def view(request):
    template = 'comments_list.html'
    with open('{}{}'.format(TEMPLATE_DIR, template)) as f:
        html = f.read()
    return Response(body=html.encode())


@app.route('^/api/regions/get/?$')
def api_get_regions(request):
    query = 'SELECT id, name FROM regions WHERE deleted=0;'
    regions = app.sql(query)[1]
    body = json.dumps(dict(regions), ensure_ascii=False)
    response = Response(body=body.encode())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('^/api/cities/get/byregion/([0-9]+)/?$')
def api_get_cities_by_region(request):
    region_id = request.params[0]
    query = 'SELECT id, name FROM cities WHERE region_id=? AND deleted=0;'
    params = (region_id,)
    cities = app.sql(query, params)[1]
    body = json.dumps(dict(cities), ensure_ascii=False)
    response = Response(body=body.encode())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('^/api/comments/get/?$')
def api_get_comments(request):
    with_names = request.GET.get('withnames', None)
    deleted = request.GET.get('deleted', 0)
    check_variables = True

    if with_names:
        try:
            with_names = int(with_names[0])
        except ValueError:
            check_variables = False

    if deleted:
        try:
            deleted = int(deleted[0])
        except ValueError:
            check_variables = False

    if not check_variables:
        return Response(
            status="400 Bad Request",
            body=b"400 Bad Request."
        )


    if with_names:
        query = (
            "SELECT c.id, c.text, c.timestamp, u.first_name, u.last_name" +
            " FROM (SELECT * FROM comments WHERE deleted=?) c" +
            " LEFT JOIN users u ON c.user_id=u.id;"
        )
    else:
        query = "SELECT * FROM comments WHERE deleted=?;"

    params = (deleted,)
    data = app.sql(query, params)[1]
    comments = {x[0]:list(x[1:]) for x in data}
    body = json.dumps(dict(comments), ensure_ascii=False)
    response = Response(body=body.encode())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('^/api/comments/delete/?$')
def api_delete_comments(request):
    if request.method == 'POST':

        bad_request = Response(
            status="400 Bad Request",
            body=b"400 Bad Request."
        )

        comment_id = request.POST.get('id', None)

        if not comment_id:
            return bad_request  # RETURN 500

        try:
            comment_id = int(comment_id[0])
        except ValueError:
            return bad_request  # RETURN 500

        query = "UPDATE comments SET deleted=1 WHERE id=?"
        params = (comment_id,)
        result = app.sql(query, params)[0]
        body = json.dumps({'success': bool(result)})
        response = Response(body=body.encode())
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('^/api/comments/delete/full/?$')
def api_delete_comments(request):
    if request.method == 'POST':

        bad_request = Response(
            status="400 Bad Request",
            body=b"400 Bad Request."
        )

        comment_id = request.POST.get('id', None)

        if not comment_id:
            return bad_request  # RETURN 500

        try:
            comment_id = int(comment_id[0])
        except ValueError:
            return bad_request  # RETURN 500

        # find user_id and delete user
        query = "SELECT user_id FROM comments WHERE id=?"
        params = (comment_id,)
        user_id = app.sql(query, params)[1][0][0]

        # delete comment from db
        query = "DELETE FROM comments WHERE id=?"
        params = (comment_id,)
        res_c = app.sql(query, params)[0]

        # delete user from db
        query = "DELETE FROM users WHERE id=?"
        params = (user_id,)
        res_u = app.sql(query, params)[0]

        body = json.dumps({'success': bool(res_c and res_u)})
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
