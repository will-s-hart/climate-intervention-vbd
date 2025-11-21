import argparse
import pathlib

import dask.diagnostics
import numpy as np
import xarray as xr
from climepi import epimod

from inputs import DATASETS, EPI_MODEL_NAME


def _run_epi_model(
    dataset=None,
    years=None,
    realizations=None,
    epi_model_name=EPI_MODEL_NAME,
):
    if years is None:
        years = DATASETS[dataset]["subset"]["years"]
    if realizations is None:
        realizations = DATASETS[dataset]["subset"]["realizations"]
    realizations = np.atleast_1d(realizations)
    save_dir = pathlib.Path(__file__).parents[1] / f"results/{dataset}_{epi_model_name}"
    epi_model = epimod.get_example_model(epi_model_name)
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
        ds_clim.sel(realization=[realization]).climepi.run_epi_model(
            epi_model, return_yearly_portion_suitable=True
        )
        for realization in realizations
    ]
    save_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        save_dir / f"{realization}_{year}.nc"
        for realization in realizations
        for year in years
    ]
    delayed_obj = xr.save_mfdataset(datasets, paths, compute=False)
    with dask.diagnostics.ProgressBar():
        delayed_obj.compute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run epi model")
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
    parser.add_argument(
        "--epi-model-name",
        type=str,
        default=None,
        help="Epi model name to run",
    )
    args = parser.parse_args()
    _run_epi_model(
        dataset=args.dataset,
        years=args.years,
        realizations=args.realizations,
        epi_model_name=args.epi_model_name,
    )
