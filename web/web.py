from flask import Flask
from flask import request
import psycopg2
import logging
import os
import json
import datetime

app = Flask(__name__)

DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVEL_KEY = "LOG_LEVEL"
DEFAULT_CONNECT_STRING = "dbname=postgres user=postgres host=localhost port=5432 password=jTYV8xQiZPvkmwV"
CONNECT_STRING_KEY = "CONNECT_STRING"
connect_string = os.environ.get(CONNECT_STRING_KEY)
connect_string = connect_string if connect_string else DEFAULT_CONNECT_STRING


def datetime_handler(date_field):
    logging.debug("Handling value '%s' of type '%s'" % (date_field, type(date_field)))
    if isinstance(date_field, datetime.date):
        return date_field.isoformat()
    raise TypeError("Unknown type")


def query(sql_query, variables):
    conn = psycopg2.connect(connect_string)
    cur = conn.cursor()
    cur.execute(sql_query, variables)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return json.dumps(results, default=datetime_handler)


# List Products
@app.route("/products")
def products():
    keyword = request.args.get('keyword', type=int)
    page_size = request.args.get('page-size', default=10, type=int)
    page = request.args.get('page', default=0, type=int)
    sql_query = ""
    params = ()
    if keyword:
        sql_query = ("select product_id, product_parent, product_title, product_category"
                     "from reviews "
                     "where product_title like '%%s%' "
                     "limit %s "
                     "offset %s ")
        params = (keyword, page_size, page)
    else:
        sql_query = ("select product_id, product_parent, product_title, product_category "
                     "from reviews "
                     "limit %s "
                     "offset %s ")
        params = (page_size, page)
    logging.debug("Using sql query: %s" % sql_query)
    logging.info("Retrieving products with keyword=%s, page=%s, and page size=%s" % (keyword, page, page_size))
    return json.dumps(query(sql_query, params))


# Reviews by Product
@app.route("/reviews/<product_id>")
def products_by_id(product_id):
    logging.info("Retrieving reviews for ID %s" % product_id)
    sql_query = "select * from reviews where product_id=%s"
    return json.dumps(query(sql_query, (product_id,)))


# Health
@app.route("/health")
def test():
    return "Server is running"


if __name__ == "__main__":
    log_level = os.environ.get(LOG_LEVEL_KEY)
    log_level = log_level if log_level else DEFAULT_LOG_LEVEL
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    app.run("0.0.0.0", 8081)
