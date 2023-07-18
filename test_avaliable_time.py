import cdsapi
import sys,os 
# block stdout
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

c = cdsapi.Client()
try:
    c.retrieve('reanalysis-era5-single-levels', {
        'product_type': 'reanalysis',
        'format': 'netcdf',
        # some far in the future
        'date': "9999-12-31",
        'time': "23:00",
    })
except Exception as e:
    # restore stdout
    sys.stdout = sys.__stdout__
    print(str(e)[-64:])


