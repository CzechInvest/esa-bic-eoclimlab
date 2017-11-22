from owslib.wfs import WebFeatureService
import atexit
import shutil
import tempfile
import os
from gdal import ogr
import json

# URL = "https://lksoftware.com.pl/geoserver/ows"
URL = "https://platform.eoclimlab.eu/geoserver/ows"
TEMPDIRS = []


def clear():
    global TEMPDIRS
    for d in TEMPDIRS:
        print("removing {}".format(d))
        shutil.rmtree(d)


atexit.register(clear)


def test_layer(tmpout, layer, results):

    print("Testing layer {}".format(layer.id))
    try:
        outfilename = os.path.join(tmpout, layer.id)
        with open(outfilename, "w") as tmpout:
            tmpout.write(w.getfeature(typename=layer.id).read())
        ds = ogr.Open(outfilename)
        layer_count = ds.GetLayerCount()
        print("\t layer count: {}".format(layer_count))

        results[layer.id]["layers"] = []
        for i in list(range(layer_count)):
            ogr_layer = ds.GetLayerByIndex(i)
            results[layer.id]["layers"].append({
                "name": ogr_layer.GetName(),
                "features": ogr_layer.GetFeatureCount()
            })
            print("\t features count for the layer {}: {}".format(
                ogr_layer.GetName(), ogr_layer.GetFeatureCount())
            )
            os.remove(outfilename)

    except Exception as e:
        results[layer.id]["error"] = "{}".format(e)
        print("Failed with exception: {}".format(e))


tmpout = tempfile.mkdtemp()
TEMPDIRS.append(tmpout)


w = WebFeatureService(URL, version="2.0.0")
results = {}
for c in w.contents:
    layer = w.contents[c]
    results[layer.id] = {}
    test_layer(tmpout, layer, results)

with open("output.json", "w") as out:
    out.write(json.dumps(results))
