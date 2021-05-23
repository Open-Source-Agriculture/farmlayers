# fsm-layers

Helper scripts for fetching and managing basic input layers for running the Farm Soil Mapping tools

Install:

```
pip install ...
```

Usage:

Make area of interest using shapely geoms:

```python
from shapely.geometry.multipolygon import MultiPolygon
from farmlayers import shp_to_boundaries

boundaries = shp_to_boundaries("boundaries.shp")
```

Download elevation:


```python
from farmlayers import download_elevation

download_elevation(geom=MultiPolygon(polygons=boundaries), dir="data")
```

Download soil related landsat 8 bands:

```python
from farmlayers import download_soil

download_soil(geom=MultiPolygon(polygons=boundaries), dir="data")
```

Download crop related landsat 8 bands


```python
from farmlayers import download_crop

download_crop(geom=MultiPolygon(polygons=boundaries), dir="data")

```