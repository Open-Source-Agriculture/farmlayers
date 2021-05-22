from datetime import datetime
from download_inputs import download_inputs
from functools import reduce
from typing import List

from shapely.geometry import Point, Polygon, MultiPolygon
from pylandsat import Catalog, Product, Scene

from geotiff import GeoTiff
from fsm.models.boundary import Boundary
from fsm.helpers.shp_converter import shpToBoundaries

import os
import numpy as np

from PIL import Image

import math


def get_paddock_polygons(file: str):
    boundaries: List[Boundary] = shpToBoundaries(file)
    polygons = [Polygon(b.mainBoundaryPoints) for b in boundaries]
    return polygons


def make_area_box(polygons: List[Polygon]):
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


def geotiff_files_first_scene():
    data_folders = os.listdir("data")
    data_folders.remove("boundary")
    scene = Scene("data/" + data_folders[0])
    available_bands = scene.available_bands()
    geotiff_list = [
        f"{scene.product_id}_B{i+1}.TIF" for i, e in enumerate(available_bands)
    ]
    geotiff_files = [os.path.join(scene.dir, g) for g in geotiff_list]

    print(scene.product_id)
    print(scene.sensor)
    print(scene.date)

    # # Access MTL metadata
    print(scene.mtl["IMAGE_ATTRIBUTES"]["CLOUD_COVER_LAND"])
    return geotiff_files


def get_tiff_array(area_box, tiff_location, crs_code=None):
    geotiff = GeoTiff(tiff_location, crs_code=crs_code)
    geotiff_array = geotiff.read_box(area_box)
    print(geotiff_array.shape)
    int_box = geotiff.get_int_box(area_box)

    # TODO distribute with dask
    to_row = np.arange(0, geotiff_array.shape[0])
    get_lon = lambda j: geotiff.get_wgs_84_coords(int_box[0][0], int_box[0][1] + j)[1]
    row = np.vectorize(get_lon)(to_row)

    to_col = np.arange(0, geotiff_array.shape[1])
    get_col = lambda i: geotiff.get_wgs_84_coords(int_box[0][0] + i, int_box[0][1])[0]
    col = np.vectorize(get_col)(to_col)

    return (geotiff_array, col, row)


def make_image(
    filename, red, green, blue, show_red=False, show_green=False, show_blue=False
):
    def normalize(a):
        return 255 * ((a - np.amin(a)) / (np.amax(a) - np.amin(a)))

    color_img_array = np.dstack(
        (
            normalize(red) * int(show_red),
            normalize(green) * int(show_green),
            normalize(blue) * int(show_blue),
        )
    )
    Image.fromarray(color_img_array.astype(np.uint8)).save(filename)


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
    print(elevation_dir)
    tiff_files = [f for f in os.listdir(elevation_dir) if f[-4:] == ".tif"]
    if len(tiff_files) > 0:
        print("WARNING! this area consists of multiple tiff files!!!")
    return os.path.join(elevation_dir, tiff_files[0])


polygons = get_paddock_polygons("data/boundary/Speed with craig.shp")
area_box = make_area_box(polygons)

# download_inputs(area_box, datetime(2020, 2, 20),  datetime(2020, 2, 22))

geotiff_files = geotiff_files_first_scene()

# red, red_row, red_col = get_tiff_array(area_box, geotiff_files[3])
# green = get_tiff_array(area_box, geotiff_files[2])
# blue = get_tiff_array(area_box, geotiff_files[1])
# nir = get_tiff_array(area_box, geotiff_files[4])
elevation, ele_col, ele_row = get_tiff_array(area_box, geotiff_elevation())

# u_gamma, u_row, u_col = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-u_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)
# k_gamma = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-k_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)
# th_gamma = get_tiff_array(area_box, "data/gamma/Radmap2019-grid-th_conc-Filtered-AWAGS_RAD_2019.tif", crs_code=4236)

from xarray import DataArray
data_array = DataArray(data=elevation.astype(np.float32), coords=[ele_row, ele_col], dims=["lat", "lon"])
ds = data_array.to_dataset(name="elevation")





new_lon = np.linspace(ds.lon[0], ds.lon[-1], ds.dims["lon"] * 2)
new_lat = np.linspace(ds.lat[0], ds.lat[-1], ds.dims["lat"] * 2)
dsi = ds.interp(lat=new_lat[1:-1], lon=new_lon[1:-1])


da = dsi.to_array(name="elevation")
new_data_array = da.assign_coords({"lon": da.lon, "lat": da.lat})

elevation_new = new_data_array[0]


make_image(
    "elevation_detailed.png",
    elevation_new,
    elevation_new,
    elevation_new,
    show_red=True,
    show_green=True,
    show_blue=True,
)


# from matplotlib import pyplot as plt
# fig, axes = plt.subplots(ncols=2, figsize=(10, 4))
# ds.air.plot(ax=axes[0])
# axes[0].set_title("Raw data")
# dsi.air.plot(ax=axes[1])
# axes[1].set_title("Interpolated data")
# plt.show()

# * make images
# make_image("red.png", red, green, blue, show_red=True)
# make_image("green.png", red, green, blue, show_green=True)
# make_image("blue.png", red, green, blue, show_blue=True)
# make_image("rgb.png", red, green, blue, show_red=True,
#            show_green=True, show_blue=True)

# make_image("nir.png", nir, nir, nir, show_red=True)
# make_ndvi_image("ndvi.png", red, nir)

# make_image("elevation.png", elevation, elevation, elevation, show_red=True,
#            show_green=True, show_blue=True)
# make_image("u_gamma.png", u_gamma, u_gamma, u_gamma, show_red=True)
# make_image("k_gamma.png", k_gamma, k_gamma, k_gamma, show_blue=True)
# make_image("th_gamma.png", th_gamma, th_gamma, th_gamma, show_green=True)
