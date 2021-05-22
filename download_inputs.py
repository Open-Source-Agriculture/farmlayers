from datetime import datetime
from typing import List, Tuple
from shapely.geometry import Point, Polygon, MultiPolygon
from pylandsat import Catalog, Product, Scene
from shapely.wkt import loads


def dates_filter(early_month, later_month, acquisition_date):
    # can make this fancier
    print(early_month, later_month, acquisition_date)
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
    scenes: List[Scene], geom: Polygon, early_month: int, later_month: int
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
    [product.download(out_dir="data") for product in products_to_download]


def download_soil(scenes, geom):
    download_month_range(scenes, geom, 10, 3)


def download_crop(scenes, geom):
    download_month_range(scenes, geom, 5, 9)


import elevation


def download_elevation(geom: Polygon):
    bounds = geom.bounds  # left, bottom, right top
    elevation.seed(cache_dir="data", bounds=bounds)


def download_inputs(
    area_box: Tuple[Tuple[float, float], Tuple[float, float]],
    begin: datetime = datetime(2020, 1, 1),
    end: datetime = datetime(2021, 1, 1),
):

    catalog = Catalog()
    geom = Polygon(
        [
            area_box[0],
            (area_box[0][0], area_box[1][1]),
            area_box[1],
            (area_box[1][0], area_box[0][1]),
        ]
    )

    scenes = catalog.search(begin=begin, end=end, geom=geom, sensors=["LE07", "LC08"])

    download_soil(scenes, geom)
    download_elevation(geom)


# product_id = scenes[5].get("product_id")
# product = Product(product_id)
# print(product.available)
# product.download(out_dir='data', files=['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'MTL.txt', 'ANG.txt'])
