EasyMapping
===========
``easymapping`` utility makes fields substitution in CSV file according to the map file stored in Google Spreadsheet.

To start working with Easy Mapping, please do the following steps:

1. Go to `<https://docs.google.com/spreadsheets/>`_ and create new mapping spreadsheet file;
2. Fill in this file by pairs [original value | new value] placed in two first columns;
3. Click Share -> Get the sharable link and paste it into MAPPING_FILE_SHARED_URL variable.

Installation
------------
Download easymapping.py and fill in MAPPING_FILE_SHARED_URL variable.

Usage
-----
.. code-block:: bash

    python3 easymapping.py [--help] [--update] [--overwrite] [--column] [file]

where:

+-----------------+--------------------------------------------------+
| argument        | description                                      |
+=================+==================================================+
| file            | editable CSV file                                |
+-----------------+--------------------------------------------------+
| -h, --help      | show this help message and exit                  |
+-----------------+--------------------------------------------------+
| -u, --update    | download and update mapping file (default False) |
+-----------------+--------------------------------------------------+
| -o, --overwrite | overwrite editable CSV file (default False)      |
+-----------------+--------------------------------------------------+
| -c, --column    | mapping column (if not set - map all columns)    |
+-----------------+--------------------------------------------------+
