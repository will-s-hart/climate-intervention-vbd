import argparse
import itertools
import pathlib

import numpy as np
import xarray as xr
from climepi import epimod
from tqdm import tqdm

from inputs import DATASETS


def _run_epi_model(
    dataset=None,
    years=None,
    realizations=None,
    epi_model_name=None,
):
    if epi_model_name is None:
        raise ValueError("epi_model_name must be provided.")
    subset_all = DATASETS[dataset]["subset"]
    if years is None:
        years = subset_all["years"]
    if realizations is None:
        realizations = subset_all["realizations"]
    years = np.atleast_1d(years)
    realizations = np.atleast_1d(realizations)

    epi_model = epimod.get_example_model(epi_model_name)

    save_dir = pathlib.Path(__file__).parents[1] / f"results/{epi_model_name}/{dataset}"
    save_dir.mkdir(parents=True, exist_ok=True)

    for year, realization in tqdm(
        itertools.product(years, realizations),
        total=len(years) * len(realizations),
    ):
        data_path = _data_path(dataset=dataset, realization=realization, year=year)
        ds_clim = xr.open_dataset(data_path, chunks={})
        ds_clim.time_bnds.load()  # Load time bounds to avoid encoding issues
        ds_epi = epi_model.run(ds_clim, return_yearly_portion_suitable=True)
        save_path = save_dir / f"{realization}_{year}.nc"
        ds_epi.to_netcdf(save_path)


def _data_path(*, dataset, realization, year):
    data_dir = DATASETS[dataset]["save_dir"]
    if "downscaled" in dataset:
        pattern = f"{dataset}_{realization}_{year}.nc"
    else:
        pattern = f"*_{year}_*_{realization}.nc"
    (path,) = data_dir.glob(pattern)
    return path


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
