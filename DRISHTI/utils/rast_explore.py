import rasterio


def raster_summary(path):

    with rasterio.open(path) as src:

        return {

            "shape": (src.height, src.width),

            "dtype": src.dtypes[0],

            "count": src.count,

            "transform": src.transform,

            "crs": src.crs,

            "bounds": src.bounds,

            "driver": src.driver,

        }