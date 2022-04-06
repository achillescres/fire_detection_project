import numpy as np
import tools as to
import troubles as tr
import classification as cls

from osgeo import gdal
gdal.UseExceptions()


# Classes
# Unknown 0
# Cloud or water 1
# Non fire 2
# 100Fire 3

# Data
modis_path = './files/mod1.hdf'
mod03_path = './files/mod03.hdf'
data = to.get_data(modis_path, mod03_path)  # Get dict with data
print('Got data')
day_time = 'day'

# Temps
t4_21 = data['t4_21']
t4_22 = data['t4_22']
t11 = data['t11']
t12 = data['t12']

# Refs
r064 = data['r064']
r085 = data['r085']
r21 = data['r21']
# Water mask
water_mask = data['water_mask']

# Customing t4
t4 = t4_22.copy()
t4_vrt = (t4_22 > 329.5) | t4_22.mask
t4[t4_vrt] = t4_21[t4_vrt]
t4.mask[t4_21.mask] = True
print('Mounted data')


nt4 = t4.data
nt4[t4.mask] = 0
tr.img(nt4)

nt11 = t11.data
nt11[t11.mask] = 0
tr.img(nt11)

ds = gdal.Open('HDF4_EOS:EOS_SWATH:"./files/mod1.hdf":MODIS_SWATH_Type_L1B:EV_1KM_Emissive')

[rows, cols] = nt11.shape
driver = gdal.GetDriverByName('GTiff')
out_ds = driver.Create('ntall.tif', cols, rows, 2, gdal.GDT_Float32)

out_band = out_ds.GetRasterBand(2)
out_band.SetDescription('T4')
out_band.WriteArray(nt4)

out_band = out_ds.GetRasterBand(1)
out_band.SetDescription('T11')
out_band.WriteArray(nt11)

out_ds.SetGeoTransform(ds.GetGeoTransform())
out_ds.SetProjection(ds.GetProjection())
out_band.FlushCache()

# def set_masks(mask):
#     t4.mask[mask] = True
#     t11.mask[mask] = True
#     t12.mask[mask] = True
#
#     r064.mask[mask] = True
#     r085.mask[mask] = True
#     r21.mask[mask] = True
#
# # Classifying
# # Blank
# classed = tr.get_ma(np.zeros(data['shape']))
# print('Created blank array')
#
# # Cloud mask
# classed = cls.cloud(day_time, classed, r064, r085, t12)
# set_masks(classed.mask)
# print('Cloud masked')
# tr.img(classed.data)
#
# # Water mask
# classed.data[water_mask] = 1
# classed.mask[water_mask] = True
# set_masks(classed.mask)
# print('Water masked')
#
# # Show water_cloud mask
# # tr.img(classed.data)
# tr.img(classed.data)
#
# # Mark non potential fire
# classed = cls.potential_fire(day_time, classed, t4, t11, r085)
# set_masks(classed.mask)
# print('Potential masked')
#
# # Absolute temp threshold
# classed = cls.absolute_fire(day_time, classed, t4)
# set_masks(classed.mask)
# print('Absolute thresholded')
# tr.img(classed.data)
# # import matplotlib.pyplot as plt
# #
# # c = np.copy(classed)
# # c[classed.mask] = 0
# #
# # plt.figure()
# # plt.hist(c.flatten(), bins=700)
# # plt.show()
