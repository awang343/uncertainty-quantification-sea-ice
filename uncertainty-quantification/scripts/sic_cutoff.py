from helpers import *
import xarray as xr

sic_data = xr.open_dataset("../data/sea_ice_concentration/amsr2_sea_ice_concentration.nc")
cropped = sic_data.isel(x=slice(100,250),y=slice(175,325))
sic = cropped["sea_ice_concentration"]

def buoyCutoff(track, dt="datetime", x="x_stere", y="y_stere"):
    new_track = track[track[dt] > pd.to_datetime("2020-04-30")]
    new_track = new_track[new_track[dt] < pd.to_datetime("2020-11-01")]

    for time, x_pos, y_pos in zip(new_track[dt], new_track[x], new_track[y]):
        conc = sic.sel(time=time, x=x_pos, y=y_pos, method="nearest").values.tolist()
        if conc < 15:
            return time
    return track[dt].iloc[-1]

result = []
valid = list(buoy_metadata()[buoy_metadata()["Interp"] == True].index)

for buoy in valid:
    result.append((buoy, buoyCutoff(buoy_data(buoy))))

pd.DataFrame(result, columns=["buoy_id", "cutoff"]).set_index("buoy_id").to_csv("../data/metadata/sic_cutoffs.csv")