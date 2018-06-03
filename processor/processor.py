from s3_downloader import S3Downloader
import unzipper
import db_initializer
import psycopg2
from multiprocessing import Process
import os
import logging

DEFAULT_DATASET_BUCKET = "amazon-reviews-pds"
DEFAULT_REMOTE_FILEPATH = "tsv/amazon_reviews_us_Home_v1_00.tsv.gz"
DEFAULT_CONNECT_STRING = "dbname=postgres user=postgres host=localhost port=5432 password=jTYV8xQiZPvkmwV"
DEFAULT_DATA_DIR = "data"
DEFAULT_LOG_LEVEL = logging.INFO

DATASET_BUCKET_KEY = "DATASET_BUCKET"
REMOTE_FILEPATH_KEY = "REMOTE_FILEPATH"
CONNECT_STRING_KEY = "CONNECT_STRING"
DATA_DIR_KEY = "DATA_DIR"
LOG_LEVEL_KEY = "LOG_LEVEL"

INSERT_SQL = ("INSERT INTO reviews ("
              "marketplace, customer_id, review_id, product_id, product_parent, product_title, "
              "product_category,  star_rating,  helpful_votes,  total_votes,  vine,  verified_purchase, "
              "review_headline,  review_body,  review_date)"
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")


def download(bucket, remote_filename, data_dir):
    downloader = S3Downloader(bucket, remote_filename, data_dir)
    downloader.download()
    local_filepath = downloader.local_filepath

    logging.info("Extracting file %s" % local_filepath)
    local_unzip_filename = unzipper.unzip_in_directory(local_filepath)

    return local_unzip_filename


def split_file(local_filename, num_files):
    logging.info("Splitting file '%s' into %s smaller files" % (local_filename, num_files))

    split_files = []
    split_filenames = []
    for part_num in range(num_files):
        split_filename = local_filename + ".part%s" % part_num
        split_file_handle = open(split_filename, 'w')
        split_files.append(split_file_handle)
        split_filenames.append(split_filename)

    f_in = open(local_filename, 'r')

    # Discard header
    f_in.readline()

    line = str(f_in.readline())
    split_file_index = 0
    while line:
        if split_file_index < num_files:
            split_files[split_file_index].write(line)
            line = str(f_in.readline())
            split_file_index = split_file_index + 1
        else:
            split_file_index = 0

    f_in.close()
    for file in split_files:
        file.close()

    return split_filenames


def read_chunk(file, chunk_size=10000):
    chunk = []
    line = file.readline()
    i = 0
    while line and i < chunk_size-1:
        chunk.append(line)
        line = file.readline()
        i = i + 1

    return chunk


def process_chunk(raw_chunk):
    clean_chunk = []
    for record in raw_chunk:
        clean_chunk.append(record)
    return clean_chunk


def write_chunk(cur, conn, clean_chunk):
    db_chunk = []
    for record in clean_chunk:
        record_tuple = tuple(record.split("\t"))
        db_chunk.append(record_tuple)
    cur.executemany(INSERT_SQL, db_chunk)
    conn.commit()


def worker(filename, connect_string):
    dataset_file = open(filename, "r")
    conn = psycopg2.connect(connect_string)
    cur = conn.cursor()

    raw_chunk = read_chunk(dataset_file)
    while len(raw_chunk) > 0:
        clean_chunk = process_chunk(raw_chunk)
        write_chunk(cur, conn, clean_chunk)
        raw_chunk = read_chunk(dataset_file)

    cur.close()
    conn.close()


def main(bucket, remote_filename, data_dir, connect_string,  num_threads=3):
    logging.info("Processor starting")
    db_initializer.setup_database(connect_string)
    extracted_filename = download(bucket, remote_filename, data_dir)
    split_filenames = split_file(extracted_filename, num_threads)
    threads = []
    for filename in split_filenames:
        t = Process(target=worker, args=(filename, connect_string))
        threads.append(t)
        t.start()


if __name__ == "__main__":
    dataset_bucket = os.environ.get(DATASET_BUCKET_KEY)
    remote_filepath = os.environ.get(REMOTE_FILEPATH_KEY)
    connect_string = os.environ.get(CONNECT_STRING_KEY)
    data_dir = os.environ.get(DATA_DIR_KEY)
    log_level = os.environ.get(LOG_LEVEL_KEY)

    dataset_bucket = dataset_bucket if dataset_bucket else DEFAULT_DATASET_BUCKET
    remote_filepath = remote_filepath if remote_filepath else DEFAULT_REMOTE_FILEPATH
    connect_string = connect_string if connect_string else DEFAULT_CONNECT_STRING
    data_dir = data_dir if data_dir else DEFAULT_DATA_DIR
    log_level = log_level if log_level else DEFAULT_LOG_LEVEL

    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    main(dataset_bucket, remote_filepath, data_dir, connect_string)
