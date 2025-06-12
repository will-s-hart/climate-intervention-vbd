import argparse
import pathlib
import time

import numpy as np
from climepi import climdata
from inputs import DATASETS
from requests.exceptions import HTTPError


def _get_data(dataset, year_range=None, realizations=None):
    kwargs = DATASETS[dataset]
    if year_range is not None:
        start_year, end_year = map(int, year_range.split("-"))
        kwargs["subset"]["years"] = list(range(start_year, end_year + 1))
    if realizations is not None:
        kwargs["subset"]["realizations"] = realizations
    return climdata.get_climate_data(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download climate data")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument(
        "--year-range", type=str, default=None, help="Years to download"
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
        year_range=args.year_range,
        realizations=args.realizations,
    )

    for realization in np.atleast_1d(args.realizations or "all"):
        download_confirmation_path = (
            pathlib.Path(__file__).parents[1] / "results/downloads/"
            f"{args.dataset}_{realization}_{args.year_range or 'all'}"
            ".txt"
        )
        download_confirmation_path.parent.mkdir(parents=True, exist_ok=True)
        with open(download_confirmation_path, "w", encoding="utf-8") as f:
            f.write("Downloaded")
