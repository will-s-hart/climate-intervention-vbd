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
):
    if realizations is None:
        realizations = DATASETS[dataset]["subset"]["realizations"]
    realizations = np.atleast_1d(realizations)
    data_dir = DATASETS[dataset]["save_dir"]
    save_dir = pathlib.Path(__file__).parents[1] / "results"
    save_dir.mkdir(parents=True, exist_ok=True)
    epi_model = epimod.get_example_model(EPI_MODEL_NAME)
    ds_clim = xr.open_mfdataset(str(data_dir / "*.nc"), data_vars="minimal", chunks={})
    ds_clim.time_bnds.load()  # Load time bounds to avoid encoding issues
    datasets = [
        ds_clim.sel(realization=[realization]).climepi.run_epi_model(
            epi_model, return_yearly_portion_suitable=True
        )
        for realization in realizations
    ]
    paths = [save_dir / f"{dataset}_{realization}.nc" for realization in realizations]
    delayed_obj = xr.save_mfdataset(datasets, paths, compute=False)
    with dask.diagnostics.ProgressBar():
        delayed_obj.compute()


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
