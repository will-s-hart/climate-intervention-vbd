import argparse
import pathlib

import numpy as np
from climepi import climdata

from inputs import DATASETS


def _get_data(dataset, years=None, realizations=None):
    if "downscaled" in dataset:
        # Downscaled data not available for direct download
        return
    kwargs = DATASETS[dataset]
    if years is not None:
        kwargs["subset"]["years"] = list(np.atleast_1d(years))
    if realizations is not None:
        kwargs["subset"]["realizations"] = list(np.atleast_1d(realizations))
    return climdata.get_climate_data(**kwargs)


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

    for realization in np.atleast_1d(args.realizations or "all"):
        for year in np.atleast_1d(args.years or "all"):
            download_confirmation_path = (
                pathlib.Path(__file__).parents[1]
                / "results/downloads"
                / args.dataset
                / f"{realization}_{year}.txt"
            )
            download_confirmation_path.parent.mkdir(parents=True, exist_ok=True)
            with open(download_confirmation_path, "w", encoding="utf-8") as f:
                f.write("Downloaded")
