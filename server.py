import os
import json
import datetime
from wsgiref.simple_server import make_server

from webframework.webframework import WebFramework, Response


TEMPLATE_DIR = '{}/templates/'.format(os.getcwd())

app = WebFramework()


@app.route('^/$')
def home(request):
    template = 'home.html'
    with open('{}{}'.format(TEMPLATE_DIR, template)) as f:
        html = f.read()
    return Response(body=html.encode())


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
        # Save user to db
        app.sql(query, params)

        user_id = app.sql('SELECT * FROM users ORDER BY id DESC LIMIT 1;')[1][0][0]

        now = datetime.datetime.now()
        query = 'INSERT INTO comments(text, user_id, timestamp) VALUES(?,?,?);'
        params = (comment_text, user_id, now)
        # Save comment to db
        app.sql(query, params)

        # Redirect to /view/
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


@app.route('^/stat/?$')
def view(request):
    template = 'statistics.html'
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
    deleted = request.GET.get('deleted', 0)

    if deleted:
        try:
            deleted = int(deleted)
        except ValueError:
            # RETURN ERROR 400
            return Response(
                status="400 Bad Request",
                body=b"400 Bad Request."
            )

    query = (
        "SELECT c.id, c.text, c.timestamp, u.first_name, u.last_name, city.name"
        " FROM (SELECT * FROM comments WHERE deleted=?) c"
        " LEFT JOIN users u, cities city"
        " ON c.user_id=u.id AND u.city_id=city.id;"
    )

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
            comment_id = int(comment_id)
        except ValueError:
            return bad_request  # RETURN 500

        # find user_id and mark as deleted user
        query = "SELECT user_id FROM comments WHERE id=?"
        params = (comment_id,)
        print(query, params)
        user_id = app.sql(query, params)[1][0][0]

        # mark comment as deleted
        query = "UPDATE comments SET deleted=1 WHERE id=?"
        params = (comment_id,)
        res_c = app.sql(query, params)[0]

        # mark user as deleted
        query = "UPDATE users SET deleted=1 WHERE id=?"
        params = (user_id,)
        res_u = app.sql(query, params)[0]

        body = json.dumps({'success': bool(res_c and res_u)})
        response = Response(body=body.encode())
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('^/api/comments/delete/full/?$')
def api_delete_comments_from_db(request):
    if request.method == 'POST':

        bad_request = Response(
            status="400 Bad Request",
            body=b"400 Bad Request."
        )

        comment_id = request.POST.get('id', None)

        if not comment_id:
            return bad_request  # RETURN 500

        try:
            comment_id = int(comment_id)
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


@app.route('^/api/statistics/?$')
def api_statistics(request):

    query = (
        "SELECT    c.name, COUNT(u.id), r.name "
        "FROM      (SELECT * FROM cities WHERE deleted=0) c "
        "LEFT JOIN (SELECT * FROM users WHERE deleted=0) u, "
        "          (SELECT * FROM regions WHERE deleted=0) r "
        "ON        u.city_id = c.id "
        "AND       c.region_id = r.id "
        "GROUP BY  c.id"
    )
    data = app.sql(query)[1]

    result = {}
    for city_name, records_count, region_name in data:
        if region_name in result:
            result[region_name].update({city_name: records_count})
        else:
            result[region_name] = {city_name: records_count}

    body = json.dumps(result, ensure_ascii=False)
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
