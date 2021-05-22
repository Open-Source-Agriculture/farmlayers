from datetime import datetime
from typing import List, Tuple
from shapely.geometry import Point, Polygon, MultiPolygon
from pylandsat import Catalog, Product, Scene
from shapely.wkt import loads
import elevation


def dates_filter(early_month: int, later_month: int, acquisition_date: datetime):
    # can make this fancier
    # print(early_month, later_month, acquisition_date)
    to_download = False
    if early_month < later_month:
        to_download = (
            acquisition_date.month > early_month
            and acquisition_date.month < later_month
        )
    else:
        to_download = (
            acquisition_date.month > later_month or acquisition_date.month < early_month
        )
    return to_download


def download_month_range(
    scenes: List[Scene], geom: Polygon, early_month: int, later_month: int, dir: str
):
    tif_poly: Polygon = loads(scenes[0]["geom"])
    filtered_scenes = [s for s in scenes if tif_poly.contains(geom)]
    products = [Product(s.get("product_id")) for s in filtered_scenes]
    acquisition_dates = [p.meta["acquisition_date"] for p in products]
    download_checks = [
        dates_filter(early_month, later_month, a_date) for a_date in acquisition_dates
    ]
    products_and_checks = list(zip(products, download_checks))
    products_to_download = [p_c[0] for p_c in products_and_checks if p_c[1]]
    [product.download(out_dir=dir) for product in products_to_download]


def download_soil(scenes, geom, dir: str):
    download_month_range(scenes, geom, 10, 3, dir)


def download_crop(scenes, geom, dir: str):
    download_month_range(scenes, geom, 5, 9, dir)


def download_elevation(geom: Polygon, dir: str):
    bounds = geom.bounds  # left, bottom, right top
    elevation.seed(cache_dir=dir, bounds=bounds)


def download_inputs(
    geom: Polygon,
    dir: str,
    begin: datetime = datetime(2020, 1, 1),
    end: datetime = datetime(2021, 1, 1),
):

    catalog = Catalog()
    scenes = catalog.search(begin=begin, end=end, geom=geom, sensors=["LE07", "LC08"])

    download_soil(scenes, geom, dir)
    download_elevation(geom, dir)
