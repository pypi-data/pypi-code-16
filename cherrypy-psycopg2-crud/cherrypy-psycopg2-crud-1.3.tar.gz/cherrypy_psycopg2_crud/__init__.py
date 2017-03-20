#   Copyright 2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import functools

import cherrypy
import psycopg2

# CrudController exposes a RESTful(ish) interface to a psycopg2 database

#       SQL     HTTP
#   C   INSERT  POST    /resource/
#   R   SELECT  GET     /resource/12?_fields=id,name
#      (or, search) /resource/?col1:like=val1&_limit=12&_offset=1&_sort=-col1,col2&_return=count,data  # noqa: E501
#   U   UPDATE  PUT     /resource/12
#   D   DELETE  DELETE  /resource/12

SQL_SEARCH_OPERATORS_TAKE_VALUE = {
    '=': True,
    '!=': True,
    '<': True,
    '<=': True,
    '>': True,
    '>=': True,

    'like': True,
    'not like': True,
    'ilike': True,
    'not ilike': True,

    '<<': True,
    '<<=': True,
    '>>': True,
    '>>=': True,

    'is null': False,
    'is not null': False,
    'is true': False,
    'is not true': False,
    'is false': False,
    'is not false': False,
}


class CrudController:
    table = None  # Subclasses should define this

    @cherrypy.expose
    @cherrypy.tools.psycopg2()
    def default(*args, **kwargs):
        # This pulling of 'self' out of args is a hacky way to avoid clashing
        # with a query string containing '?self=abc'.
        self = args[0]
        args = args[1:]

        if args:
            object_id = args[0]
        else:
            object_id = None

        method = cherrypy.request.method.upper()
        is_index = cherrypy.request.is_index

        collection = bool(is_index and not object_id)
        item = bool(not is_index and object_id)

        if len(args) > 1:
            raise cherrypy.HTTPError(404)

        cherrypy.response.headers['Content-Type'] = 'application/json'

        if method == "POST":
            if collection:
                return self.create(kwargs)
        elif method == "GET":
            if collection:
                return self.search(kwargs)
            elif item:
                return self.read(object_id, kwargs)
            elif not is_index:
                collection_url = cherrypy.url(
                    path=cherrypy.request.path_info + "/",
                    qs=cherrypy.request.query_string)
                raise cherrypy.HTTPRedirect(collection_url, 301)
        elif method == "PUT":
            if item:
                return self.update(object_id, kwargs)
        elif method == "DELETE":
            if item:
                return self.delete(object_id)

        raise cherrypy.HTTPError(405)

    def create(self, parameters):
        request_record = parse_request_body_json_object()

        columns = []
        values = []
        sql_parameters = []

        for row in request_record:
            columns.append(row['key'])
            values.append("%s")
            sql_parameters.append(row['value'])

        columns_sql = ", ".join(columns)
        values_sql = ", ".join(values)

        insert_sql = (
            "INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING id")

        insert_sql = insert_sql.format(
            table=quote_identifier(self.table), columns=columns_sql,
            values=values_sql)

        cursor = cherrypy.request.psycopg2_cursor
        error_handling_sql_execute(cursor, insert_sql, sql_parameters)

        if cursor.rowcount != 1:
            raise cherrypy.HTTPError(400)

        object_id = cursor.fetchone()['id']

        return self.read(object_id, parameters)

    def read(self, object_id, parameters):
        columns_sql = parameters_to_columns_sql(parameters)

        sql = (
            "WITH results AS (SELECT {columns} FROM {table} WHERE "
            "id=%(object_id)s) "
            "SELECT row_to_json(results)::text AS result FROM results")
        sql = sql.format(
            columns=columns_sql, table=quote_identifier(self.table))

        cursor = cherrypy.request.psycopg2_cursor
        error_handling_sql_execute(cursor, sql, {'object_id': object_id})

        if cursor.rowcount != 1:
            raise cherrypy.HTTPError(404)

        result = cursor.fetchone()['result']
        return result.encode()

    def search(self, parameters):
        columns_sql = parameters_to_columns_sql(parameters)
        (where_sql, sql_parameters) = parameters_to_where_sql(parameters)
        sort_sql = parameters_to_sort_sql(parameters)
        limit_sql = parameters_to_limit_sql(parameters)
        offset_sql = parameters_to_offset_sql(parameters)
        return_types = parameters_to_return_types(parameters)

        sql_calculations = {}
        sql_params = []

        if 'count' in return_types:
            sql_calculations["count_calc"] = "SELECT count(*) AS count FROM {table} {where}"
            sql_params.extend(sql_parameters)

        if 'data' in return_types:
            sql_calculations["data_calc"] = "WITH results AS (SELECT {columns} FROM {table} {where} {sort} {limit} {offset}) SELECT coalesce(json_agg(row_to_json(results)), '[]'::json) AS data FROM results"  # noqa: E501
            sql_params.extend(sql_parameters)

        if not sql_calculations:
            raise cherrypy.HTTPError(400, "No valid return types")

        sql_calculation_strs = []
        for key, value in sql_calculations.items():
            sql_calc_str = "{key} AS ({value})".format(key=key, value=value)
            sql_calculation_strs.append(sql_calc_str)

        sql_calculations_str = "WITH " + ", ".join(sql_calculation_strs)

        sql_results_str = " CROSS JOIN ".join(sql_calculations)
        if len(sql_calculations) > 1:
            sql_results_str = "(" + sql_results_str + ")"

        sql = sql_calculations_str + " SELECT row_to_json(result)::text AS result FROM " + sql_results_str + " AS result"  # noqa: E501

        sql = sql.format(
            columns=columns_sql, table=quote_identifier(self.table),
            where=where_sql, sort=sort_sql, limit=limit_sql, offset=offset_sql)

        cursor = cherrypy.request.psycopg2_cursor
        error_handling_sql_execute(cursor, sql, sql_params)

        result = cursor.fetchone()['result']
        return result.encode()

    def update(self, object_id, parameters):
        request_record = parse_request_body_json_object()

        set_segments = []

        sql_parameters = []

        for row in request_record:
            set_segments.append("{}=%s".format(row['key']))
            sql_parameters.append(row['value'])

        set_sql = ', '.join(set_segments)

        update_sql = "UPDATE {table} SET {set} WHERE id=%s"
        sql_parameters.append(object_id)

        update_sql = update_sql.format(
            table=quote_identifier(self.table), set=set_sql)

        cursor = cherrypy.request.psycopg2_cursor
        error_handling_sql_execute(cursor, update_sql, sql_parameters)

        if cursor.rowcount != 1:
            raise cherrypy.HTTPError(404)

        return self.read(object_id, parameters)

    def delete(self, object_id):
        sql = "DELETE FROM {table} WHERE id=%(object_id)s"
        sql = sql.format(table=quote_identifier(self.table))

        cursor = cherrypy.request.psycopg2_cursor
        error_handling_sql_execute(cursor, sql, {'object_id': object_id})

        if cursor.rowcount != 1:
            raise cherrypy.HTTPError(404)

        return


def error_handling_sql_execute(cursor, operation, parameters=None):
    try:
        cursor.execute(operation, parameters)
    except psycopg2.Error as e:
        cherrypy.log.error("Database operation failed\n", traceback=True)
        msg = "Database operation failed: {!r}"
        error_detail = None
        if e.pgerror:
            error_detail = e.pgerror.split("\n")[0].strip()
        raise cherrypy.HTTPError(400, msg.format(error_detail))


@functools.lru_cache()
def quote_identifier(unquoted_identifier):
    sql = "SELECT quote_ident(%(unquoted_identifier)s) AS quoted_identifier"

    cursor = cherrypy.request.psycopg2_cursor
    error_handling_sql_execute(
        cursor, sql, {'unquoted_identifier': unquoted_identifier})

    return cursor.fetchone()['quoted_identifier']


def parameters_to_columns_sql(parameters):
    fields = parameters.get('_fields')
    if not fields:
        return '*'

    columns = []
    for field in fields.split(','):
        columns.append(quote_identifier(field.strip()))

    return ", ".join(columns)


def parameters_to_where_sql(parameters):
    sql_parameters = []

    and_segments = []

    for key, value in parameters.items():
        if key.startswith('_'):
            continue

        key_operator = key.split(':', 1)

        if len(key_operator) == 2:
            key, operator = key_operator
        else:
            operator = '='

        identifier = quote_identifier(key)

        if not isinstance(value, list):
            value = [value]

        or_segments = []

        operator_takes_value = SQL_SEARCH_OPERATORS_TAKE_VALUE.get(
            operator)

        if operator_takes_value is None:
            raise cherrypy.HTTPError(400, 'unknown search operator')

        for val in value:
            or_segment = "{} {}".format(identifier, operator)

            if operator_takes_value:
                or_segment += " %s"
                sql_parameters.append(val)

            or_segments.append(or_segment)

        and_segments.append(" OR ".join(or_segments))

    if and_segments:
        return ("WHERE (" + ") AND (".join(and_segments) + ")", sql_parameters)
    else:
        return ("", [])


def parameters_to_sort_sql(parameters):
    sort = parameters.get('_sort')
    if not sort:
        return ""

    sort_exprs = []

    for key in sort.split(','):
        order = 'ASC'
        if key.startswith('-'):
            order = 'DESC'
            key = key[1:]

        identifier = quote_identifier(key)

        sort_exprs.append("{} {}".format(identifier, order))

    return "ORDER BY {}".format(', '.join(sort_exprs))


def parameters_to_limit_sql(parameters):
    limit = parameters.get('_limit')
    if not limit:
        return ""

    try:
        limit = int(limit)
    except ValueError:
        raise cherrypy.HTTPError(400, 'limit must be numeric')

    return "LIMIT {}".format(limit)


def parameters_to_offset_sql(parameters):
    offset = parameters.get('_offset')
    if not offset:
        return ""

    try:
        offset = int(offset)
    except ValueError:
        raise cherrypy.HTTPError(400, 'offset must be numeric')

    return "OFFSET {}".format(offset)


def parameters_to_return_types(parameters):
    return_types = parameters.get('_return')
    if not return_types:
        return ['data', 'count']

    return [rt.strip() for rt in return_types.split(',')]


def parse_request_body_json_object():
    if cherrypy.request.body.content_type.value != 'application/json':
        raise cherrypy.HTTPError(415, "Expected JSON body data")

    cursor = cherrypy.request.psycopg2_cursor
    json_data = cherrypy.request.body.read().decode()

    parse_json_sql = (
        "SELECT quote_ident(key) AS key, value FROM "
        "json_each(%(json)s)")

    error_handling_sql_execute(
        cursor, parse_json_sql, {'json': json_data})

    if cursor.rowcount < 1:
        raise cherrypy.HTTPError(400, "Expected non-empty JSON object")

    return cursor.fetchall()
