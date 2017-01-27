#!/usr/bin/python3
import os
import re
import csv
import argparse
import urllib3

__author__ = 'Serhii Kostel'

# type your sharable link here
MAPPING_FILE_SHARED_URL = ''

FIRST_START_DESCRIPTION = '''
Easy Mapping utility makes fields substitution in CSV file according to the map file stored in Google Spreadsheet.

To start working with Easy Mapping, please do the following steps:
 1. Go to https://docs.google.com/spreadsheets/ and create new mapping spreadsheet file;
 2. Fill in this file by pairs [original value | new value] placed in two first columns;
 3. Click Share -> Get the sharable link and paste it into MAPPING_FILE_SHARED_URL variable.
'''
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.EasyMapping')


def get_download_csv_url():
    """Convert google doc shared edit url to export url."""
    return '{0}/export?format=csv'.format(MAPPING_FILE_SHARED_URL.rsplit('/', 1)[0])


def get_local_map_file():
    """Extract doc ID from shared url."""
    matched_id = re.match('https://docs\.google\.com/.+/d/([\w\d-]*)/.+', MAPPING_FILE_SHARED_URL)

    if not matched_id:
        raise ValueError('Wrong MAPPING_FILE_SHARED_URL value.')

    file_id = matched_id.group()
    return os.path.join(CONFIG_DIR, 'mapping_{0}.csv'.format(file_id))


def update_mapping_file():
    """Download and store mapping file from docs.google.com."""
    download_url = get_download_csv_url()
    local_map_file = get_local_map_file()

    http = urllib3.PoolManager()
    resp = http.request('GET', download_url)

    if resp.status >= 400:
        raise ValueError(u'Wrong response from [{0}]: {1} ({2})'.format(
            resp.status, resp.data.decode('utf-8'), download_url))

    os.makedirs(os.path.dirname(local_map_file), exist_ok=True)
    with open(local_map_file, 'wb') as mfp:
        mfp.write(resp.data)

    print('Mapping file successfully updated!')


def load_mapping():
    """Return dict based on the first two rows of local mapping CSV file."""
    local_map_file = get_local_map_file()

    if not os.path.exists(local_map_file):
        update_mapping_file()

    mapping, unique_keys = dict(), set()

    with open(local_map_file, newline='') as csv_map:
        for num, row in enumerate(csv.reader(csv_map)):
            if len(row) < 2:
                raise ValueError(u'Wrong columns number: {0} < 2'.format(len(row)))

            key, value = row[0:2]

            if not key:
                print(u'Warning! Empty key in the row #{0}. Skipping...'.format(num))
                continue

            if key in unique_keys:
                print(u'Warning! Found not unique key [{0}] '
                      u'in the row #{1} with value "{2}". Skipping...'.format(key, num, value))
                continue

            mapping[key] = value
            unique_keys.add(value)

    return mapping


def csv_mapping(csv_file, overwrite=False):
    """Make CSV file with mapped values according to the mapping file."""
    mapped_csv_file = '{0}.emap.csv'.format(os.path.splitext(csv_file)[0])
    mapping = load_mapping()

    with open(csv_file, newline='') as csv_in:
        with open(mapped_csv_file, 'w', newline='') as csv_out:

            csv_reader = csv.reader(csv_in)
            csv_writer = csv.writer(csv_out, quoting=csv.QUOTE_MINIMAL)

            for num, row in enumerate(csv_reader):
                csv_writer.writerow([mapping.get(value.strip(), value) for value in row])
                if num % 1000 == 0:
                    print('.', end='')

    print(' Done!')

    if overwrite:
        print('Overwrite CSV file "{0}"'.format(csv_file))
        os.rename(mapped_csv_file, csv_file)


if __name__ == '__main__':

    if not MAPPING_FILE_SHARED_URL:
        print('Google drive mapping file url not specified.')
        print(FIRST_START_DESCRIPTION)
        exit(1)

    parser = argparse.ArgumentParser(description='CSV file mapping based on '
                                                 'google doc file "{0}"'.format(MAPPING_FILE_SHARED_URL))
    parser.add_argument('file', type=str, nargs='?',
                        default=None,  help='editable CSV file')
    parser.add_argument('--update', '-u', action="store_true",
                        default=False, help='download and update mapping file (default False)')
    parser.add_argument('--overwrite', '-o', action="store_true",
                        default=False, help='overwrite editable CSV file (default False)')
    args = parser.parse_args()

    if args.update:
        try:
            update_mapping_file()
        except Exception as err:
            print('Error update mapping file: {0}'.format(err))

    if args.file is not None:
        if not (args.file.endswith('.csv') and os.path.exists(args.file)):
            print('Wrong CSV file {0}.'.format(args.file))
            exit(1)

        try:
            csv_mapping(args.file, args.overwrite)
        except Exception as err:
            print('Error on CSV mapping: {0}'.format(err))
