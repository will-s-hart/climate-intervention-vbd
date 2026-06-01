import argparse
import itertools
import pathlib

import numpy as np
from climepi import climdata
from tqdm import tqdm

from inputs import DATASETS


def _get_data(dataset, years=None, realizations=None):
    kwargs_all = DATASETS[dataset]
    subset_all = kwargs_all["subset"]
    if years is None:
        years = subset_all["years"]
    if realizations is None:
        realizations = subset_all["realizations"]
    years = np.atleast_1d(years)
    realizations = np.atleast_1d(realizations)

    download_confirmation_dir = (
        pathlib.Path(__file__).parents[1] / "results/downloads" / dataset
    )
    download_confirmation_dir.mkdir(parents=True, exist_ok=True)

    for year, realization in tqdm(
        itertools.product(years, realizations),
        total=len(years) * len(realizations),
    ):
        subset_current = {
            **subset_all,
            "years": [year],
            "realizations": [realization],
        }
        kwargs_current = {**kwargs_all, "subset": subset_current}
        if "downscaled" not in dataset:
            # Downscaled data not available for direct download
            climdata.get_climate_data(**kwargs_current)
        download_confirmation_path = (
            download_confirmation_dir / f"{realization}_{year}.txt"
        )
        with open(download_confirmation_path, "w", encoding="utf-8") as f:
            f.write("Downloaded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download climate data")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument(
        "--years", type=int, nargs="+", default=None, help="Years to download"
    )
    parser.add_argument(
        "--realizations",
        type=int,
        nargs="+",
        default=None,
        help="Realizations to download",
    )

    args = parser.parse_args()

    _get_data(
        dataset=args.dataset,
        years=args.years,
        realizations=args.realizations,
    )
