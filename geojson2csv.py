import json
import csv
import argparse
import os
import datetime
import brotli
import requests


def decode(filename):
    basename = "output"
    if filename.startswith("https://") or filename.startswith("http://"):
        r = requests.get(filename, allow_redirects=True)
        s = r.content
        basename = os.path.basename(r.request.path_url).rsplit(".", 2)[0]
    else:
        with open(filename, "rb") as f:
            s = f.read()
        if filename.endswith(".br"):
            try:
                s = brotli.decompress(s)
            except Exception:
                print(f"{filename} is already decompressed")
                pass
        basename = os.path.basename(filename).rsplit(".", 2)[0]

    geojson_data = json.loads(s)
    if geojson_data["type"] == "FeatureCollection":
        with open(basename + ".csv", "w") as f:
            parse_feature_collection(geojson_data["features"], f)
    else:
        print(
            "Can currently only parse FeatureCollections, but I found ",
            geojson_data["type"],
            " instead",
        )


def parse_feature_collection(features, outfile):
    csvwriter = csv.writer(outfile, lineterminator=os.linesep)

    count = 0
    header = []
    for feature in features:
        if (
            feature["geometry"]["type"] != "Point"
        ):  # skip LineString in radiosonde ascent
            continue
        # append a readable timestamp (time is just Unix epoch)
        feature["properties"]["datetime"] = datetime.datetime.fromtimestamp(
            feature["properties"]["time"]
        )
        if count == 0:
            header = list(feature["properties"].keys())
            # append coords
            header.extend(["lon", "lat", "alt"])
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(feature_to_row(feature, feature["properties"].keys()))
    outfile.close()


def feature_to_row(feature, header):
    l = []
    for k in header:
        l.append(feature["properties"][k])
    if feature["geometry"]["type"] != "Point":
        raise RuntimeError(
            "Expecting point type, but got ", feature["geometry"]["type"]
        )
    coords = feature["geometry"]["coordinates"]
    assert len(coords) == 3
    l.extend(coords)
    return l


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="geojson2csv.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert GeoJSON to CSV",
        epilog="""\
<file> can be a local filename, or a http://<uri>  
If the filename has a .br extension, it will be automatically brotli-decompressed.
The result will be written to <basename of file>.csv .

Examples:
    python geojson2csv.py 11240_20221104_040000.geojson
    python geojson2csv.py https://ims.windy.com/radiosonde/data/station/11/035/2022/11/fm94/11035_20221104_120000.geojson.br
    """,
    )
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    for f in args.files:
        decode(f)
