TABLE_NAME = "schema_table"

JSON_TYPE_TO_ATHENA_TYPE = {
    # string
    ("string", None): "string",
    ("string", "date-time"): "timestamp",
    ("string", "date-time-string"): "string",
    ("string", "date"): "date",
    ("string", "date-string"): "string",
    ("string", "time"): "time",
    ("string", "time-string"): "string",
    ("string", "decimal"): "decimal",
    # number
    ("number", None): "double",
    ("number", "double"): "double",
    ("number", "float"): "float",
    ("number", "decimal"): "decimal",
    # integer
    ("integer", None): "integer",
    ("integer", "date-time"): "timestamp",
    ("integer", "date"): "date",
    ("integer", "time"): "time",
    # boolean
    ("boolean", None): "boolean",
    # array
    ("array", None): "array",
    # object
    ("object", None): "struct",
}


def _build_query(field, json_schema):
    """
        Description
            Extract the columns names and types of a JSON Schema
        Args
            json_schema (String): A JSON schema.
            field (String):A key of the JSON Schema to be the first point of iteration.
    """

    # If we are on the first layer, then access the 'properties' key
    if json_schema.get("$schema") is not None:
        return _build_query(field, json_schema.get('properties'))

    if json_schema.get('properties') is not None:
        sql = _build_query(field, json_schema.get('properties'))

        # for nested fields we normalize the sql by removing newlines
        sql = " ".join(sql.split()).replace(' ', ':')
        if field:
            return '{field} struct<{inner_columns}>'.format(
                field=field, inner_columns=sql
            )
        else:
            return "struct<{inner_columns}>".format(inner_columns=sql)

    # if items are available, we are within an array and need to recurse again
    if json_schema.get('items') is not None:
        # pass None as field name to prevent it from appearing in inner column sql
        sql = _build_query(None, json_schema.get('items'))

        # for nested fields we normalize the sql by removing newlines
        sql = " ".join(sql.split())

    # if we are within an object (ie. type doesn't exist), we need to iterate over all fields
    if json_schema.get('type') is None:
        first = True
        sql = ""
        for field in json_schema:
            if not first:
                sql += ","
            sql += _build_query(field, json_schema[field])
            first = False

        return sql

    # if we are within a field, we can create a column
    key = (json_schema['type'], json_schema.get('format', None))
    sql_type = JSON_TYPE_TO_ATHENA_TYPE[key]

    if field:
        return '{field} {sql_type}'.format(field=field, sql_type=sql_type)
    else:
        return "{sql_type}".format(sql_type=sql_type)