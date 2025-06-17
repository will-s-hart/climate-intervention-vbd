import argparse
import pathlib

import dask.diagnostics
from climepi import epimod
from download_data import _get_data
from inputs import EPI_MODEL_NAME


def _run_epi_model(
    dataset=None,
    realizations=None,
):
    ds_clim = _get_data(dataset=dataset, realizations=realizations)
    epi_model = epimod.get_example_model(EPI_MODEL_NAME)
    for realization in ds_clim.realization.values:
        print(f"Running epi model for dataset {dataset}, realization {realization}")
        ds_epi_curr = ds_clim.sel(realization=[realization]).climepi.run_epi_model(
            epi_model, return_yearly_portion_suitable=True
        )
        path_curr = (
            pathlib.Path(__file__).parents[1] / f"results/{dataset}_{realization}.nc"
        )
        delayed_obj = ds_epi_curr.to_netcdf(path_curr, compute=False)
        with dask.diagnostics.ProgressBar():
            delayed_obj.compute()
        print(f"Saved results to {path_curr}")


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
    args = parser.parse_args()
    _run_epi_model(dataset=args.dataset, realizations=args.realizations)
