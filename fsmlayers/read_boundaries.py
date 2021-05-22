from shapely.geometry import Polygon, MultiPolygon  # type: ignore
from typing import List  # type: ignore
from geojson import load  # type: ignore
import shapefile  # type: ignore


def geojson_to_boundaries(file: str) -> List[Polygon]:
    geojson_f = open(file, "r")
    gj = load(geojson_f)

    boundaries = []

    if gj["type"] == "FeatureCollection":
        for feature in gj["features"]:
            if feature["geometry"]["type"] == "Polygon":
                paddock_id = feature["properties"]["name"]
                print(feature["geometry"]["coordinates"])
                boundary = Polygon(lonLatData=feature["geometry"]["coordinates"])
                boundaries.append(boundary)

    return boundaries


def shp_to_boundaries(file: str) -> List[Polygon]:
    """Takes a shape file and returns a list of boundary(s)

    Args:
        file (str): location if the shp file

    Returns:
        List[Polygon]: a list of boundary(s)
    """
    myshp = open(file, "rb")

    sf = shapefile.Reader(shp=myshp)
    if sf.shapeType != 5:
        errmsg = "Must provide a shape file of type POLYGON"
        raise Exception(errmsg)
    else:
        boundaries = []
        shapes = sf.shapes()
        for i in range(len(shapes)):
            s = sf.shape(i)
            parts = s.parts
            parts.reverse()
            points = s.points
            outList = []
            for part in parts:
                outList.append(points[part:])
                points = points[:part]
            outList.reverse()
            poly = Polygon(outList[0], holes=outList[1:])
            boundaries.append(poly)
        return boundaries
