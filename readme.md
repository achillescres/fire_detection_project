Чтобы воспользоваться программой нужно указать пути к hdf файлам(снимки желательно спутника AQUA).
Или можно воспользоваться файлами из папки example(можно просто нажимать Enter ничего не вводя ни в одно поле)

Выходные данные: 
    1. Датасет с потенциально горящими пикселами(каждый пиксел на снимках MOD021KM это участок земли 1 км * 1 км)
    2. GeoTiff с потенциально горящими пикселами
    3. txt файл с логами о геометрии пикелей в формате WKT, возможны ошибки если не использовать aoi


Чтобы использовать нужен python 3.7 с установленным gdal, numpy, pandas, matplotlib. Рекомендую дистрибутив anaconda/miniconda.

conda create -n fire_env python=3.7
conda activate fire_env
conda install gdal -c conda-forge
conda install numpy matplotlib pandas
