# import os
import json
import datetime
from pathlib import Path
from wsgiref.simple_server import make_server

from webframework.webframework import WebFramework, Response


TEMPLATE_DIR = Path('templates')
TMPL_HOME = TEMPLATE_DIR / 'home.html'
TMPL_VIEW = TEMPLATE_DIR / 'comments_list.html'
TMPL_COMMENT = TEMPLATE_DIR / 'comment.html'
TMPL_STAT = TEMPLATE_DIR / 'statistics.html'

with TMPL_HOME.open() as f:
    TEMPLATE_HOME = f.read()

with TMPL_VIEW.open() as f:
    TEMPLATE_VIEW = f.read()

with TMPL_COMMENT.open() as f:
    TEMPLATE_COMMENT = f.read()

with TMPL_STAT.open() as f:
    TEMPLATE_STAT = f.read()


app = WebFramework()


@app.route('^/$')
def home(request):
    return Response(body=TEMPLATE_HOME.encode())


@app.route('^/comment/?$')
def comment(request):

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

    return Response(body=TEMPLATE_COMMENT.encode())


@app.route('^/view/?$')
def view(request):
    return Response(body=TEMPLATE_VIEW.encode())


@app.route('^/stat/?$')
def view(request):
    return Response(body=TEMPLATE_STAT.encode())


@app.route('^/api/regions/get/?$')
def api_get_regions(request):
    query = 'SELECT id, name FROM regions WHERE deleted=0;'
    regions = app.sql(query)[1]
    response = Response.as_json(dict(regions))
    return response


@app.route('^/api/cities/get/byregion/([0-9]+)/?$')
def api_get_cities_by_region(request):
    region_id = request.params[0]
    query = 'SELECT id, name FROM cities WHERE region_id=? AND deleted=0;'
    params = (region_id,)
    cities = app.sql(query, params)[1]
    response = Response.as_json(dict(cities))
    return response


@app.route('^/api/comments/get/?$')
def api_get_comments(request):
    deleted = request.GET.get('deleted', 0)

    if deleted:
        try:
            deleted = int(deleted)
        except ValueError:
            return app.bad_request() # RETURN ERROR 400

    query = (
        "SELECT c.id, c.text, c.timestamp, u.first_name, u.last_name, city.name "
        "FROM (SELECT * FROM comments WHERE deleted=?) c "
        "LEFT JOIN users u, cities city "
        "ON c.user_id=u.id AND u.city_id=city.id;"
    )

    params = (deleted,)
    data = app.sql(query, params)[1]
    comments = {k:v for k, *v in data}
    response = Response.as_json(comments)
    return response


@app.route('^/api/comments/delete/?$')
def api_delete_comments(request):
    if request.method == 'POST':

        comment_id = request.POST.get('id', None)

        if not comment_id:
            return app.bad_request()  # RETURN 400

        try:
            comment_id = int(comment_id)
        except ValueError:
            return app.bad_request()  # RETURN 400

        # find user_id and mark as deleted user
        query = "SELECT user_id FROM comments WHERE id=?"
        params = (comment_id,)
        user_id = app.sql(query, params)[1][0][0]

        # mark comment as deleted
        query = "UPDATE comments SET deleted=1 WHERE id=?"
        params = (comment_id,)
        res_c = app.sql(query, params)[0]

        # mark user as deleted
        query = "UPDATE users SET deleted=1 WHERE id=?"
        params = (user_id,)
        res_u = app.sql(query, params)[0]

        response = Response.as_json({'success': bool(res_c and res_u)})
        return response


@app.route('^/api/comments/delete/full/?$')
def api_delete_comments_from_db(request):
    if request.method == 'POST':

        comment_id = request.POST.get('id')

        if not comment_id:
            return app.bad_request()  # RETURN 400

        try:
            comment_id = int(comment_id)
        except ValueError:
            return app.bad_request()  # RETURN 400

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

        response = Response.as_json({'success': bool(res_c and res_u)})
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

    response = Response.as_json(result)
    return response


if __name__ == '__main__':
    try:
        httpd = make_server('', 8000, app)
        print('Serving on port 8000...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
