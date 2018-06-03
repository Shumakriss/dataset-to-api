import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os.path
import sys
import logging

class S3Downloader:

    def __init__(self, bucket, remote_filepath, data_dir):
        self.bucket = bucket
        self.total_downloaded_bytes = 0
        self.last_download_percentage = 0
        self.dataset_size = 0
        # This S3 bucket is public and does not require credentials to download
        s3_public_config = Config(signature_version=UNSIGNED)
        self.s3 = boto3.client('s3', config=s3_public_config)
        self.s3_dataset_filepath = remote_filepath
        self.local_filepath = os.path.join(data_dir, remote_filepath.replace("tsv/", ""))

    def progress_callback(self, bytes):
        self.total_downloaded_bytes = self.total_downloaded_bytes + bytes
        download_percentage = self.total_downloaded_bytes / self.dataset_size * 100
        if download_percentage - self.last_download_percentage > 10:
            logging.info("Download %s percent complete" % int(download_percentage))
            self.last_download_percentage = download_percentage

    def check_remote_file(self):
        objects = self.s3.list_objects(Bucket=self.bucket, Prefix=self.s3_dataset_filepath)

        if "Contents" not in objects:
            raise Exception
        if len(objects["Contents"]) != 1:
            raise Exception
        if objects["Contents"][0]["Key"] != self.s3_dataset_filepath:
            raise Exception

        return objects["Contents"][0]["Size"]

    def download(self):
        logging.info("Checking for downloaded file named %s" % self.local_filepath)
        if os.path.isfile(self.local_filepath):
            logging.info("File already downloaded: %s" % self.local_filepath)
            return

        self.dataset_size = self.check_remote_file()
        size_in_mb = self.dataset_size / 1024 / 1024

        logging.info("Beginning download of %s MB dataset file" % int(size_in_mb))
        self.s3.download_file(self.bucket, self.s3_dataset_filepath, self.local_filepath,
                              Callback=self.progress_callback)
        logging.info("Download complete")
        return self.local_filepath
