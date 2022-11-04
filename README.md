# geojson-to-csv
A basic GeoJSON to CSV parser

## Usage

Convert GeoJSON to CSV

positional arguments:
  _files_

optional arguments:
  -h, --help  show this help message and exit

_file_ can be a local filename, or a https:// uri  
If the filename has a .br extension, it will be automatically brotli-decompressed.
the resulting csv filename will be name <basename of file>.csv .

Examples:

>    python geojson2csv.py 11240_20221104_040000.geojson
>    python geojson2csv.py https://ims.windy.com/radiosonde/data/station/11/035/2022/11/fm94/11035_20221104_120000.geojson.br
    
