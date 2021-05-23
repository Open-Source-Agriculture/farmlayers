# Farm Layers [early stages of dev]

Helper scripts for fetching and managing basic geotiff files related to Farm Mapping

Supports:

- elevation
- red bands
- blue bands
- green bands
- near-inferred bands

Coming:

Australian Radiometric data
- k gamma
- u gamma
- th gamma

Install:

```
pip install farmlayers
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