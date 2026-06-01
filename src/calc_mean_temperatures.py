import argparse
import itertools
import pathlib

import climepi  # noqa
import numpy as np
import xarray as xr
import xcdat.spatial  # noqa
from tqdm import tqdm

from inputs import DATASETS
from run_epi_model import _data_path


def _calc_mean_temperatures(
    dataset=None,
    years=None,
    realizations=None,
):
    subset_all = DATASETS[dataset]["subset"]
    if years is None:
        years = subset_all["years"]
    if realizations is None:
        realizations = subset_all["realizations"]
    years = np.atleast_1d(years)
    realizations = np.atleast_1d(realizations)

    save_dir = (
        pathlib.Path(__file__).parents[1] / f"results/mean_temperatures/{dataset}"
    )
    save_dir.mkdir(parents=True, exist_ok=True)

    for year, realization in tqdm(
        itertools.product(years, realizations),
        total=len(years) * len(realizations),
    ):
        data_path = _data_path(dataset=dataset, realization=realization, year=year)
        ds_clim = xr.open_dataset(data_path, chunks={})
        ds_clim.time_bnds.load()  # Load time bounds to avoid encoding issues
        ds_mean = (
            ds_clim.spatial.average("temperature")[["temperature"]]
            .compute()
            .climepi.yearly_average()
        )
        save_path = save_dir / f"{realization}_{year}.nc"
        ds_mean.to_netcdf(save_path)


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
