import gzip
import shutil
import os.path
import logging


def unzip_in_directory(input_filename):
    logging.info("Checking for unzipped file")
    output_filename = input_filename.replace('.gz', '')
    if os.path.isfile(output_filename):
        logging.info("File %s already unzipped" % input_filename)
        return output_filename

    logging.info("Unzipping dataset file %s to %s" % (input_filename, output_filename))

    with gzip.open(input_filename, 'rb') as f_in:
        with open(output_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_filename
