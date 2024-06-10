"""First downloads ERA5 data to file. Then projects onto a polar stereographic grid centered on the North Pole."""
import cdsapi
import xarray as xr
import os
import numpy as np
import pandas as pd
import pyproj
from urllib.request import urlopen
import xesmf as xe

# Settings
start_dates = [m.strftime('%Y-%m-%d') for m in pd.date_range('2019-10-01', '2020-10-01', freq='1MS')]
end_dates = [m.strftime('%Y-%m-%d') for m in pd.date_range('2019-10-01', '2020-10-01', freq='1ME')]
savename = 'era5_mosaic_period'

saveloc = '../data/era5/'
saveloc_regridded = '../data/era5_regridded/'
download = True
regrid = False

sfc_var_list = ['mean_sea_level_pressure',
                '10m_u_component_of_wind',
                '10m_v_component_of_wind',
                'total_cloud_cover',
                'total_column_cloud_liquid_water',
                'total_column_cloud_ice_water']

if download:
    for start_date, end_date in zip(start_dates, end_dates):
        c = cdsapi.Client(verify=True)
        params = {'product_type': 'reanalysis',
                  'format': 'netcdf',
                  'variable': sfc_var_list,
                  'date': list(pd.date_range(start_date, end_date, freq='1D').strftime('%Y-%m-%d')),
                  'time': list(map("{:02d}:00".format, range(0,24))),
                  'area': [90, -180, 50, 180]}
    
        fl = c.retrieve('reanalysis-era5-single-levels', params)
        saveloc = '../data/era5/'
        with urlopen(fl.location) as f:
            with xr.open_dataset(f.read()) as ds:
                ds.to_netcdf(saveloc + savename + '_' + start_date.strftime('%Y%m%d') + '.nc',
                             encoding={var: {'zlib': True}
                                          for var in ds.variables()})

if regrid:
    # TBD: Refactor this code to (a) create a dataset with all the original variables still in it
    # and (b) join all the monthly data.

    # Open first file to get lat/lon grid
    with xr.open_dataset(saveloc +  savename + '_' + '20191001' + '.nc') as ds_msl:
        lon = ds_msl.longitude
        lat = ds_msl.latitude
        lon2d, lat2d = np.meshgrid(lon, lat)
    
    # Set resolution for output
    dx = 25e3
    xgrid = np.arange(-2e6, 2e6+1, dx)
    xgrid, ygrid = np.meshgrid(xgrid, xgrid)
    
    proj_LL = 'epsg:4326' # WGS 84 Ellipsoid
    proj_XY = 'epsg:3413' # NSIDC Polar Stereographic
    transform_to_ll = pyproj.Transformer.from_crs(proj_XY, proj_LL, always_xy=True)
    
    longrid = np.zeros(xgrid.shape)
    latgrid = np.zeros(xgrid.shape)
    for ii in range(xgrid.shape[0]):
        for jj in range(xgrid.shape[1]):
            lonij, latij = transform_to_ll.transform(xgrid[ii, jj], ygrid[ii, jj])
            longrid[ii, jj] = lonij
            latgrid[ii, jj] = latij

    for start_date in start_dates:
        with xr.open_dataset(saveloc +  savename + '_' + '20191001' + '.nc') as ds: 
            for var in ['msl', 'u10', 'v10']: # TBD: Get the short names for the cloud variables
                attrs = ds.attrs
                ds_in = xr.Dataset({var: (('time', 'xc', 'yc'), ds[var].data)},
                                   coords={'time': (('time',), ds['time'].data),
                                           'lon': (('xc', 'yc'), lon2d),
                                           'lat': (('xc', 'yc'), lat2d)})
        
                ds_out = xr.Dataset(coords={'lon': (('xc', 'yc'), longrid),
                                            'lat': (('xc', 'yc'), latgrid)})
                regridder = xe.Regridder(ds_in, ds_out, "bilinear")
                ds_regridded = regridder(ds_in)
        
                if var == 'msl':
                    valid = ds_regridded['msl'] > 0
                ds_regridded[var] = ds_regridded[var].where(valid)
                ds_regridded = ds_regridded.assign_coords({'x_stere': (('xc', 'yc'), xgrid),
                                        'y_stere': (('xc', 'yc'), ygrid)})
                for x in ds_regridded.attrs:
                    attrs[x] = ds_regridded.attrs[x]
        
                attrs['crs'] = proj_XY
                ds_regridded.attrs = attrs
                ds_regridded.rename({'lon': 'longitude', 'lat': 'latitude'})
                # TBD: Add to a dictionary and then merge them before saving
                ds_regridded.to_netcdf(saveloc_regridded + 'era5_' + var + '_regridded_' + savename + '.nc',
                             encoding={v: {'zlib': True}
                                          for v in [var, 'longitude', 'latitude']})
