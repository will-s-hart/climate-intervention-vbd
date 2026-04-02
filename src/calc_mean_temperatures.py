import argparse
import pathlib

import climepi  # noqa
import dask.diagnostics
import numpy as np
import xarray as xr
import xcdat.spatial  # noqa

from inputs import DATASETS


def _calc_mean_temperatures(
    dataset=None,
    years=None,
    realizations=None,
):
    if years is None:
        years = DATASETS[dataset]["subset"]["years"]
    if realizations is None:
        realizations = DATASETS[dataset]["subset"]["realizations"]
    realizations = np.atleast_1d(realizations)
    save_dir = (
        pathlib.Path(__file__).parents[1] / f"results/mean_temperatures/{dataset}"
    )
    ds_clim = xr.open_mfdataset(
        str(DATASETS[dataset]["save_dir"] / "*.nc"),
        data_vars="minimal",
        coords="minimal",
        compat="override",
        chunks={},
    )
    ds_clim = ds_clim.sel(realization=realizations).isel(
        time=ds_clim.time.dt.year.isin(years)
    )
    ds_clim.time_bnds.load()  # Load time bounds to avoid encoding issues
    datasets = [
        ds_clim.sel(realization=[realization])
        .isel(time=ds_clim.time.dt.year.isin([year]))
        .spatial.average("temperature")[["temperature"]]
        .compute()
        .climepi.yearly_average()
        for realization in realizations
        for year in years
    ]
    paths = [
        save_dir / f"{realization}_{year}.nc"
        for realization in realizations
        for year in years
    ]
    save_dir.mkdir(parents=True, exist_ok=True)
    delayed_obj = xr.save_mfdataset(datasets, paths, compute=False)
    with dask.diagnostics.ProgressBar():
        delayed_obj.compute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate mean temperatures")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=None,
        help="Years to run the epi model for",
    )
    parser.add_argument(
        "--realizations",
        type=int,
        nargs="+",
        default=None,
        help="Realizations to run the epi model on",
    )
    args = parser.parse_args()
    _calc_mean_temperatures(
        dataset=args.dataset,
        years=args.years,
        realizations=args.realizations,
    )
