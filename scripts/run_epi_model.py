import argparse
import pathlib
import tempfile

import dask.diagnostics
import dask.distributed
import xarray as xr
from climepi import epimod
from inputs import DATASETS, EPI_MODEL_NAME


def _run_epi_model(
    dataset=None,
):
    ds_clim = xr.open_mfdataset(
        str(pathlib.Path(DATASETS[dataset]["save_dir"]) / "*.nc"),
        data_vars="minimal",
        chunks={},
    )
    ds_clim.time_bnds.load()
    epi_model = epimod.get_example_model(EPI_MODEL_NAME)
    temp_dir = tempfile.TemporaryDirectory(suffix="_climepi")
    for realization in ds_clim.realization.values:
        print(f"Running epi model for realization: {realization}")
        delayed_obj = (
            ds_clim.sel(realization=[realization])
            .climepi.run_epi_model(epi_model, return_yearly_portion_suitable=True)
            .to_netcdf(
                pathlib.Path(temp_dir.name) / f"{realization}.nc",
                compute=False,
            )
        )
        with dask.diagnostics.ProgressBar():
            delayed_obj.compute()
    print("Combining results from all realizations")
    ds_epi = xr.open_mfdataset(
        str(pathlib.Path(temp_dir.name) / "*.nc"),
        data_vars="minimal",
        chunks={},
    )
    ds_epi.time_bnds.load()
    delayed_obj = ds_epi.to_netcdf(
        pathlib.Path(__file__).parents[1] / f"results/{dataset}.nc", compute=False
    )
    with dask.diagnostics.ProgressBar():
        delayed_obj.compute()
    temp_dir.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run epi model")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    args = parser.parse_args()
    _run_epi_model(dataset=args.dataset)
