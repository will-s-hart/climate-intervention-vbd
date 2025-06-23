import argparse
import pathlib

import dask.diagnostics
import numpy as np
import xarray as xr
from climepi import epimod
from inputs import DATASETS, EPI_MODEL_NAME


def _run_epi_model(
    dataset=None,
    realizations=None,
    epi_model_name=EPI_MODEL_NAME,
):
    if realizations is None:
        realizations = DATASETS[dataset]["subset"]["realizations"]
    realizations = np.atleast_1d(realizations)
    save_dir = pathlib.Path(__file__).parents[1] / f"results/{epi_model_name}"
    epi_model = epimod.get_example_model(epi_model_name)
    ds_clim = xr.open_mfdataset(
        str(DATASETS[dataset]["save_dir"] / "*.nc"), data_vars="minimal", chunks={}
    ).sel(realization=realizations)
    ds_clim.time_bnds.load()  # Load time bounds to avoid encoding issues
    if epi_model_name == "kaye_ae_aegypti_niche":
        ds_clim = _precipitation_rolling_average(
            ds_clim, dataset=dataset, realizations=realizations
        )
    datasets = [
        ds_clim.sel(realization=[realization]).climepi.run_epi_model(
            epi_model, return_yearly_portion_suitable=True
        )
        for realization in realizations
    ]
    save_dir.mkdir(parents=True, exist_ok=True)
    paths = [save_dir / f"{dataset}_{realization}.nc" for realization in realizations]
    delayed_obj = xr.save_mfdataset(datasets, paths, compute=False)
    with dask.diagnostics.ProgressBar():
        delayed_obj.compute()


def _precipitation_rolling_average(ds_clim, dataset=None, realizations=None):
    if dataset == "glens_feedback":
        # 2019 values come from control run, so append them
        ds_clim_2019 = (
            xr.open_mfdataset(
                str(DATASETS["glens_control"]["save_dir"] / "*.nc"),
                data_vars="minimal",
                chunks={},
            )
            .assign_coords(scenario=["sai"])
            .sel(time="2019", realization=realizations)
        )
        ds_clim_2019.time_bnds.load()
        ds_clim = xr.concat([ds_clim, ds_clim_2019], dim="time")
    ds_clim = ds_clim.assign(
        precipitation=ds_clim["precipitation"].rolling(time=30).mean(),
    )
    # Drop data for years in which rolling avg for first 30 days not available
    years = ds_clim.time.dt.year
    jump_years = [years.min().item()] + list(
        years.where(years.diff("time", label="upper") > 1, drop=True).values
    )
    ds_clim = ds_clim.drop_isel(time=years.isin(jump_years))
    return ds_clim


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run epi model")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument(
        "--realizations",
        type=int,
        nargs="+",
        default=None,
        help="Realizations to run the epi model on",
    )
    parser.add_argument(
        "--epi-model-name",
        type=str,
        default=None,
        help="Epi model name to run",
    )
    args = parser.parse_args()
    _run_epi_model(
        dataset=args.dataset,
        realizations=args.realizations,
        epi_model_name=args.epi_model_name,
    )
