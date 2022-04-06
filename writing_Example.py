tr.img(t11)
nt11 = t11.data
nt11[t11.mask] = 0
tr.img(nt11)
ds = gdal.Open('HDF4_EOS:EOS_SWATH:"./files/mod1.hdf":MODIS_SWATH_Type_L1B:EV_1KM_Emissive')

[rows, cols] = nt11.shape
driver = gdal.GetDriverByName('GTiff')
out_ds = driver.Create('nt11.tif', cols, rows, 2, gdal.GDT_Float32)
out_band = out_ds.GetRasterBand(1)
out_band.WriteArray(nt11)
out_band = out_ds.GetRasterBand(2)
out_band.WriteArray(nt4)
out_ds.SetGeoTransform(ds.GetGeoTransform())
out_ds.SetProjection(ds.GetProjection())
out_band.FlushCache()

del out_band
out_ds = None
del ds