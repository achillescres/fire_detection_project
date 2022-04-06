import numpy as np
import tools as to

from osgeo import gdal
gdal.UseExceptions()


def array2file(arr, file_tag, file_name, parent_path):
    driver = gdal.GetDriverByName(file_tag)

    [rows, cols] = arr.shape
    out_ds = driver.Create(
        f"./output/{file_name}", cols, rows, 1, gdal.GDT_Float32
    )
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(arr)
    out_band.FlushCache()

    del out_band

    parent_ds = gdal.Open(parent_path)
    out_ds.SetGeoTransform(parent_ds.GetGeoTransform())
    out_ds.SetProjection(parent_ds.GetProjection())

    out_ds = None
    parent_ds = None

    print('Success')


def arrays2file(arrs, file_tag, file_name, parent_path):
    driver = gdal.GetDriverByName(file_tag)

    [rows, cols] = arrs[0].shape

    out_ds = driver.Create(
        f"./output/{file_name}", cols, rows, len(arrs), gdal.GDT_Float32
    )
    for i, arr in enumerate(arrs):
        out_band = out_ds.GetRasterBand(i + 1)
        out_band.WriteArray(arr)
        out_band.FlushCache()

        del out_band

    parent_ds = gdal.Open(parent_path)
    out_ds.SetGeoTransform(parent_ds.GetGeoTransform())
    out_ds.SetProjection(parent_ds.GetProjection())

    out_ds = None
    parent_ds = None

    print('Success')


class FirePixel:
    def __init__(self, i, j, latlon, polygon, V):
        self.i = i
        self.j = j
        self.n = i * (j + 1) + j + 1
        self.latlon = latlon
        self.polygon = polygon

    @property
    def b_wkt(self):
        return 'POLY'

    @property
    def b_latlon(self):
        return self.latlon[0], self.latlon[1]


def write_answer(ijs, latlons, polygons, t4, t11):
    pixels = []
    for i in range(len(ijs)):
        pixels.append(
            FirePixel(ijs[i], latlons[i], polygons[i],
                      t4[ijs[i][0], ijs[i][1]],
                      t11[ijs[i][0], ijs[i][1]])
        )

    write_to_csv
