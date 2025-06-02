import argparse
import pathlib

import dask.diagnostics
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
    with dask.diagnostics.ProgressBar():
        ds_epi = (
            ds_clim.climepi.run_epi_model(
                epi_model, return_yearly_portion_suitable=True
            ).compute()  # For some reason next step stalls if not computed here (may be
            # fixed in next xcdat version; using Dask distributed scheduler may also
            # help)
        )
    ds_epi.to_netcdf(pathlib.Path(__file__).parents[1] / f"results/{dataset}.nc")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run epi model")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    args = parser.parse_args()
    _run_epi_model(dataset=args.dataset)
