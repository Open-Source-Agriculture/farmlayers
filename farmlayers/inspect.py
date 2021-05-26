from datetime import datetime
from functools import reduce
from typing import Dict, List

from shapely.geometry import Point, Polygon, MultiPolygon
from pylandsat import Catalog, Product, Scene

from geotiff import GeoTiff



import os
import numpy as np

from PIL import Image

import math



def make_area_box(polygons: List[Polygon]):
    # TODO use multi polygon instead
    right = math.inf
    top = -math.inf
    left = -math.inf
    bottom = math.inf
    for p in polygons:
        if p.bounds[0] < right:
            right = p.bounds[0]
        if p.bounds[3] > top:
            top = p.bounds[3]
        if p.bounds[2] > left:
            left = p.bounds[2]
        if p.bounds[1] < bottom:
            bottom = p.bounds[1]
    return ((right, top), (left, bottom))


def geotiff_files_first_scene(dir: str) -> Dict[str, List[str]]:
    data_folders = [d for d in os.listdir(dir) if "LC08" in d]
    scenes_dict = dict([(df, Scene(os.path.join(dir, df))) for df in data_folders])
    def get_geotiff_files(scene: Scene):
        available_bands = scene.available_bands()
        geotiff_list = [
            f"{scene.product_id}_B{i+2}.TIF" for i, e in enumerate(available_bands)
        ]
        geotiff_files = [os.path.join(scene.dir, g) for g in geotiff_list]
        return(geotiff_files)
    geotiff_files_dict = dict([(d, get_geotiff_files(s)) for d, s in scenes_dict.items()])

    return geotiff_files_dict


def get_tiff_array(area_box, tiff_location, crs_code=None):
    geotiff = GeoTiff(tiff_location, crs_code=crs_code)
    geotiff_array = geotiff.read_box(area_box)
    # int_box = geotiff.get_int_box(area_box)

    # # TODO distribute with dask
    # to_row = np.arange(0, geotiff_array.shape[0])
    # get_lon = lambda j: geotiff.get_wgs_84_coords(int_box[0][0], int_box[0][1] + j)[1]
    # row = np.vectorize(get_lon)(to_row)

    # to_col = np.arange(0, geotiff_array.shape[1])
    # get_col = lambda i: geotiff.get_wgs_84_coords(int_box[0][0] + i, int_box[0][1])[0]
    # col = np.vectorize(get_col)(to_col)

    return (geotiff_array)


def make_image(red, green, blue, show_red=False, show_green=False, show_blue=False
) -> Image:
    def normalize(a):
        return 255 * ((a - np.amin(a)) / (np.amax(a) - np.amin(a)))

    color_img_array = np.dstack(
        (
            normalize(red) * int(show_red),
            normalize(green) * int(show_green),
            normalize(blue) * int(show_blue),
        )
    )
    return Image.fromarray(color_img_array.astype(np.uint8)) #.save(filename)


def make_ndvi_image(filename, red, nir):
    ndvi = (nir - red) / (nir + red)
    lower = -0.1
    upper = 0.6

    def normalize(a):
        return 255 * ((a - lower) / (upper - lower))

    ndvi_normalized = normalize(ndvi)
    color_img_array = np.dstack(
        (
            np.amax(ndvi_normalized) - ndvi_normalized,
            ndvi_normalized,
            ndvi_normalized * 0,
        )
    )
    Image.fromarray(color_img_array.astype(np.uint8)).save(filename)


def geotiff_elevation():
    elevation_zones_dir = "data/SRTM1/cache/"
    elevation_dir_name = os.listdir(elevation_zones_dir)[0]
    elevation_dir = os.path.join(elevation_zones_dir, elevation_dir_name)
    tiff_files = [f for f in os.listdir(elevation_dir) if f[-4:] == ".tif"]
    if len(tiff_files) > 0:
        print("WARNING! this area consists of multiple tiff files!!!")
    return os.path.join(elevation_dir, tiff_files[0])


def inspect_images(dir: str, geom: MultiPolygon, out_dir: str=""):
    """Tool for inspecting the images. Useful to make sure there isn't any cloud cover.

    Args:
        dir (str): Directory where the data is stored
        geom (MultiPolygon): Area of interest
    """
    print("WARNING! this is unstable!")
    for k, geotiff_files in geotiff_files_first_scene(dir).items():
        print(f"Building: {k}")
        b = geom.bounds
        area_box = ((b[0], b[3]), (b[2], b[1]))
        red = get_tiff_array(area_box, geotiff_files[3])
        green = get_tiff_array(area_box, geotiff_files[2])
        blue = get_tiff_array(area_box, geotiff_files[1])
        # nir = get_tiff_array(area_box, geotiff_files[4])
        img = make_image(red, green, blue, show_red=True, show_green=True, show_blue=True)
        img.save(os.path.join(out_dir, f"{k}.png"))


# polygons = get_paddock_polygons("data/boundary/Speed with craig.shp")
# area_box = make_area_box(polygons)

# download_inputs(area_box, datetime(2020, 2, 20),  datetime(2020, 2, 22))

# geotiff_files = geotiff_files_first_scene()

# red, red_row, red_col = get_tiff_array(area_box, geotiff_files[3])
# green = get_tiff_array(area_box, geotiff_files[2])
# blue = get_tiff_array(area_box, geotiff_files[1])
# nir = get_tiff_array(area_box, geotiff_files[4])
# elevation, ele_col, ele_row = get_tiff_array(area_box, geotiff_elevation())

# u_gamma, u_row, u_col = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-u_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)
# k_gamma = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-k_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)
# th_gamma = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-th_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)
