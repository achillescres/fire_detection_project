import numpy as np
import tools as to
import troubles as tr
import classification as cls
import writer

import matplotlib.pyplot as plt

from osgeo import gdal
gdal.UseExceptions()


# Classes
# Unknown 0
# Cloud or water 1
# Non fire 2
# 100Fire 3

# Data
modis_path = './files/mod1.hdf'  # DONT CHANGE THIS!
mod03_path = './files/mod03.hdf'  # DONT CHANGE THIS!
data = to.get_data('./files/mod1.hdf', './files/mod03.hdf')  # DONT CHANGE THIS!
print('Got data')
day_time = 'day'

fires = cls.classify_fires(data, day_time)
tr.img(fires, 'LOL')


driver = gdal.GetDriverByName('GTiff')

# [cols, rows] = fires.shape
# out_ds = driver.Create("fires.tif", cols, rows, 1, gdal.GDT_Float32)
# print('t4_22', tr.counter(data['t4_22'].data))
# writer.arrays2file(
#     [fires, data['t4_21'], data['t4_22'], data['r064'], data['r085']],
#     'GTiff', 'fires.tif', modis_path
# )

fires_ij = np.dstack(np.where(fires == 1))
fires_latlon = to.get_fires_latlon(fires)
fires_polygons = to.get_polygons(fires_ij)


writer.write_answer(fires_ij, fires_latlon, fires_polygons)
# print(writer.get_fires_latlon(fires))
