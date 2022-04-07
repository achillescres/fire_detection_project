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
    def __init__(self, i, j, latlon, polygon, t4, t11):
        self.i = i
        self.j = j
        self.latlon = latlon  # 0 lat 1 lon
        self.polygon = polygon
        self.t4 = t4
        self.t11 = t11

    def get_dict(self):
        d = dict()

        d['col'] = self.j + 1
        d['row'] = self.i + 1
        d['latitude'] = self.latlon[0]
        d['longitude'] = self.latlon[1]
        d['T4'] = self.t4
        d['T11'] = self.t11

        poly_coords = ' '.join([f"{ll[0]} {ll[1]}," for ll in self.polygon])[:-1]
        d['pixel_poly'] = f'"POLYGON (({poly_coords}))"'
        print(d['pixel_poly'])

        return d


def write_answer(region, imageid, ijs, latlons, polygons, t4, t11):
    pixels = []
    for i in range(len(ijs)):
        pixels.append(
            FirePixel(*ijs[i], latlons[i], polygons[i],
                      t4[ijs[i][0], ijs[i][1]],
                      t11[ijs[i][0], ijs[i][1]])
        )

    print(*pixels, sep='\n')

    write_to_csv(region, imageid, pixels)


def write_to_csv(region, imageid, pixels):
    [print('|' * 120) for i in range(8)]
    print('WRITING CSV')
    print(f"Writing {len(pixels)} pixels")
    print(f"Go...")

    import pandas as pd

    data = []
    for i, pixel in enumerate(pixels):
        data.append({
            **pixel.get_dict(),
            'IMAGEID': imageid,
            'region': region,
            'N': i + 1,
        })

    columns = ['IMAGEID', 'N', 'col', 'row', 'longitude', 'latitude',
               'T4', 'T11', 'pixel_poly', 'region']

    df = pd.DataFrame(data, columns=columns)
    print(df)

    df.to_csv('./output/ans.csv', index=False)

    s = f"GEOMETRYCOLLECTION({', '.join([i['pixel_poly'][1:-1] for i in data])})"
    print(s)
    with open('./output/wktg.txt', 'w') as f:
        f.write(s)


def cut(fires, modis_path):
    array2file(fires, 'GTiff', './outpu/local_cut.tif', modis_path)

    OutTile = gdal.Warp("./output/local_cut.tif",
                        "./output/final_cut.tif",
                        cutlineDSName='./files/aoi.shp',
                        cropToCutline=True,
                        dstNodata=0)

    OutTile = None

    fires = gdal.Open("./output/final_cut.tif").ReadAsArray()
    return fires
