import numpy as np
import matplotlib.pyplot as plt

from osgeo import gdal
gdal.UseExceptions()


def get_zenith_array(sd):
    zenith_ds = gdal.Open(sd)

    format = 'JP2OpenJPEG'
    driver = gdal.GetDriverByName(format)

    dst_ds = driver.CreateCopy('zenith.jp2', zenith_ds, 0)

    zenith_ds = None
    dst_ds = None


def get_ma(band, mask=False):
    if type(mask) not in ('numpy.ma.core.MaskedArray', 'numpy.ndarray'):
        mask = np.full(band.shape, False)

    return np.ma.masked_array(band, mask)


def mask_it(img):
    d = img
    # if 'mask' in dir(img):
    #     d = img.data
    #     d[img.mask] = np.nan

    return d


def img(img, title):
    # plt.figure()

    def scale_minmax(img):
        return img  # (img - np.nanmin(img)) / (np.nanmax(img) + np.nanmin(img))

    plt.imshow(scale_minmax(mask_it(img)), cmap=plt.cm.Greys)
    plt.title(title)
    plt.show()


def hist(img, title):
    print(counter(img))
    d = mask_it(img)

    d = d.flatten()
    plt.hist(d, bins=500)
    plt.title(title)
    plt.show()


def counter(img):
    img = mask_it(img)
    unique, counts = np.unique(img, return_counts=True)
    return dict(zip(unique, counts))
