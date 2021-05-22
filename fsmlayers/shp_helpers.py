from typing import List
import shapefile

from geojson import Polygon, MultiPolygon

class Boundary(object):
    def __init__(self, lonLatData: list, boundsBox: list = None):
        """Boundary

        Args:
            latLonData (list): [[x,y]...[x,y]]
            boundsBox (list): [minx, miny, maxx, maxy]
        """
        self.lonLatData = lonLatData 
        self.geojson_polygon: Polygon = Polygon(coordinates=self.lonLatData)
        self.latLonData = [[[l[1], l[0]] for l in lst] for lst in lonLatData]
        self.mainBoundaryPoints = lonLatData[0]
        (self.mainBoundaryPoints)
        self.boundaryAdditionalParts = lonLatData[1:]
        (self.boundaryAdditionalParts)
        if boundsBox == None:
            lons = [p[0] for p in self.mainBoundaryPoints]
            lats = [p[1] for p in self.mainBoundaryPoints]
            self.boundsBox = [min(lons), min(lats), max(lons), max(lats)]
        else:
            self.boundsBox = boundsBox


def shpToBoundaries(shpFile: str) -> List[Boundary]:
    """Takes a shape file and returns a list of Boundary(s)

    Args:
        shpFile (str): location if the shp file

    Returns:
        List[Boundary]: a list of Boundary(s)
    """
    myshp = open(shpFile, "rb")

    sf = shapefile.Reader(shp=myshp)
    # For getting the bounding box
    boundaries = []
    if sf.shapeType != 5:
        errmsg ="Must provide a shape file of type POLYGON"
        raise Exception(errmsg)
    else:
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
            # List[List[List[Tuple[float,float]]]]
            boundaries.append(Boundary(outList, s.bbox))
    return(boundaries)
        

def shpToBoundary(shpFile: str) -> Boundary:
    """Uses the first polygon in the shp file to create a Boundary

    Args:
        shpFile (str): location if the shp file

    Returns:
        Boundary: Boundary object
    """
    myshp = open(shpFile, "rb")

    sf = shapefile.Reader(shp=myshp)
    # For getting the bounding box
    boundaries = []
    if sf.shapeType != 5:
        errmsg ="Must provide a shape file of type POLYGON"
        raise Exception(errmsg)
    else:
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
            # List[List[List[Tuple[float,float]]]]
            boundaries.append(Boundary(outList, s.bbox))
    return(boundaries[0])
        