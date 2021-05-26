import datetime as DT
from datetime import datetime
import os
from typing import List, Tuple, Union
from shapely.geometry import Point, Polygon, MultiPolygon
from pylandsat import Catalog, Product, Scene
from shapely.wkt import loads
import elevation
import shutil



tif_translate_dict = {
    "B2.TIF": "blue.tif",
    "B3.TIF": "green.tif",
    "B4.TIF": "red.tif",
    "B5.TIF": "nir.tif",
}

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
            (acquisition_date.month > early_month) or (acquisition_date.month < later_month)
        )
    return to_download


def download_month_range(
    scenes: List[Scene], geom: Polygon, early_month: int, later_month: int, dir: str
):
    tif_poly: Polygon = loads(scenes[0]["geom"]) # TODO get more scenes !!!!
    filtered_scenes = [s for s in scenes if tif_poly.contains(geom)]
    products = [Product(s.get("product_id")) for s in filtered_scenes]
    acquisition_dates = [p.meta["acquisition_date"] for p in products]
    # [print(p.available) for p in products]
    download_checks = [
        dates_filter(early_month, later_month, a_date) for a_date in acquisition_dates
    ]
    products_and_checks = list(zip(products, download_checks))
    products_to_download = [p_c[0] for p_c in products_and_checks if p_c[1]]
    for product in products_to_download:
        print(product.available)

        product.download(out_dir=dir, files=['B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'MTL.txt'])
        # # script to rename files
        # date_path = os.path.join(dir , product.product_id)
        # for tif_file in os.listdir(date_path):
        #     tif_path = os.path.join(date_path, tif_file)
        #     tif_suffix = tif_file[-6:]
        #     new_file = os.path.join(date_path, tif_translate_dict[tif_suffix])
        #     os.rename(tif_path, new_file)
        # new_dir = os.path.join(dir ,product.product_id.split("_")[3])
        # os.rename(os.path.join(dir, product.product_id), new_dir)


def download_soil(
    geom: Union[Polygon, MultiPolygon], 
    dir: str,
    begin: datetime = datetime.now() - DT.timedelta(days=365),
    end: datetime = datetime.now(),
    ):

    catalog = Catalog()
    scenes = catalog.search(begin=begin, end=end, geom=geom, sensors=["LC08"])
    download_month_range(scenes, geom, 11, 3, dir)


def download_crop(
    geom: Union[Polygon, MultiPolygon], 
    dir: str,
    begin: datetime = datetime.now() - DT.timedelta(days=365),
    end: datetime = datetime.now(),
    ):

    catalog = Catalog()
    scenes = catalog.search(begin=begin, end=end, geom=geom, sensors=["LC08"])
    download_month_range(scenes, geom, 5, 10, dir)


def download_elevation(geom: Polygon, dir: str):
    bounds = geom.bounds  # left, bottom, right top
    elevation.seed(cache_dir=dir, bounds=bounds)
    cache_dir = os.path.join(dir, "SRTM1/cache")
    c_dir = os.listdir(cache_dir)[0]
    c_files = os.listdir(os.path.join(cache_dir, c_dir))
    c_elevation = [f for f in c_files if f[-4:]==".tif"][0]
    c_path = os.path.join(os.path.join(cache_dir, c_dir), c_elevation)
    os.rename(c_path, os.path.join(dir, "elevation.tif"))
    shutil.rmtree(os.path.join(dir, "SRTM1"))

