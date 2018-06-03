import psycopg2
import logging

CHECK_TABLE_EXISTS_SQL = ("SELECT EXISTS ("
                              "SELECT 1 "
                              "FROM   information_schema.tables "
                              "WHERE  table_schema = 'public' "
                              "AND    table_name = 'reviews' );")

CREATE_TABLE_SQL = ("CREATE TABLE public.reviews"
                            "("
                            "marketplace character varying(4) COLLATE pg_catalog.default,"
                            "customer_id integer,"
                            "review_id character varying(14) COLLATE pg_catalog.default,"
                            "product_id character varying(10) COLLATE pg_catalog.default,"
                            "product_parent integer,"
                            "product_title text,"
                            "product_category character varying(4) COLLATE pg_catalog.default,"
                            "star_rating integer,"
                            "helpful_votes integer,"
                            "total_votes integer,"
                            "vine \"char\","
                            "verified_purchase \"char\","
                            "review_headline character varying(255) COLLATE pg_catalog.default,"
                            "review_body text,"
                            "review_date date"
                            ")")

MAX_DB_CONNECT_TRIES = 5


def setup_database(connect_string):
    logging.info("Checking database setup for connect string '%s'" % connect_string)
    conn = psycopg2.connect(connect_string)
    logging.info("Successful connection to database made")
    cur = conn.cursor()
    cur.execute(CHECK_TABLE_EXISTS_SQL)
    table_exists, = cur.fetchone()
    if not table_exists:
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        logging.info("Table 'reviews' was created.")
    else:
        logging.info("Table 'reviews' already exists")

    cur.close()
    conn.close()
