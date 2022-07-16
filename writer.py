import json

import numpy as np
import tools as to

from osgeo import gdal, ogr
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

    parent_ds = None
    out_ds = None
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
    def __init__(self, i, j, latlon, polygon, t4, t11):
        self.i = i
        self.j = j
        self.latlon = latlon  # 0 lat 1 lon
        self.polygon = polygon
        self.t4 = t4
        self.t11 = t11
        self.region = 'UNKNOWN'

    def get_dict(self):
        d = dict()

        d['col'] = self.j + 1
        d['row'] = self.i + 1
        d['latitude'] = self.latlon[0]
        d['longitude'] = self.latlon[1]
        d['T4'] = self.t4
        d['T11'] = self.t11
        d['region'] = self.region
        poly_coords = ' '.join([f"{ll[0]} {ll[1]}," for ll in self.polygon])[:-1]
        d['pixel_poly'] = f'POLYGON (({poly_coords}))'
        print(d['pixel_poly'])
        print(d['pixel_poly'])

        return d


def write_answer(region, imageid, ijs, latlons, polygons, t4, t11, aoi_path: str):
    pixels = []
    for i in range(len(ijs)):
        pixels.append(
            FirePixel(*ijs[i], latlons[i], polygons[i],
                      t4[ijs[i][0], ijs[i][1]],
                      t11[ijs[i][0], ijs[i][1]])
        )

    pixels = filter_with_aoi(pixels, aoi_path)
    print(*pixels, sep='\n')

    write_to_csv(region, imageid, pixels)


def write_to_csv(region, imageid, pixels):
    [print('|' * 120) for i in range(12)]
    print('WRITING CSV')
    print(f"Writing {len(pixels)} pixels")
    print(f"Go...")

    import pandas as pd

    data = []
    for i, pixel in enumerate(pixels):
        data.append({
            **pixel.get_dict(),
            'IMAGEID': imageid,
            'N': i + 1,
        })
        print(data[i]['pixel_poly'])

    columns = ['IMAGEID', 'N', 'col', 'row', 'longitude', 'latitude',
               'T4', 'T11', 'pixel_poly', 'region']

    df = pd.DataFrame(data, columns=columns)
    print(df)

    df.to_csv('./output/ans.csv', index=False)

    s = f"GEOMETRYCOLLECTION({', '.join([i['pixel_poly'][1:-1] for i in data])})"
    print(s)
    with open('./output/wktg.txt', 'w') as f:
        f.write(s)


def filter_with_aoi(pixels, aoi_path):
    if not aoi_path:
        return pixels

    from osgeo import ogr

    aoi_ds = ogr.Open(aoi_path)
    # first feature of the shapefile
    aoi_layer = aoi_ds.GetLayer()

    inner_pixels = []
    for index, pixel in enumerate(pixels):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint((pixel.polygon[0][0] + pixel.polygon[1][0]) / 2, (pixel.polygon[0][1] + pixel.polygon[1][1]) / 2)
        aoi_layer.SetSpatialFilter(point)

        if aoi_layer.GetFeatureCount() != 0:
            for i in aoi_layer:
                region = i.GetField('name')
                break

            pixel.region = region
            inner_pixels.append(pixel)

        aoi_layer.SetSpatialFilter(None)

    aoi_ds = None
    aoi_layer = None
    return inner_pixels
