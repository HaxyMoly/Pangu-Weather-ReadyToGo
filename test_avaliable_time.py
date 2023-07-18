import cdsapi


c = cdsapi.Client()
c.retrieve('reanalysis-era5-single-levels', {
    'product_type': 'reanalysis',
    'format': 'netcdf',
    # some far in the future
    'date': "9999-12-31",
    'time': "23:00",
})

