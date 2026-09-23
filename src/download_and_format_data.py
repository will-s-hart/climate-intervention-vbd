import argparse
import itertools
import pathlib

import numpy as np
import xarray as xr
import xcdat.bounds  # noqa
from climepi import climdata
from tqdm import tqdm

from inputs import DATASETS, get_climate_data_path, get_downscaled_raw_data_path


def _download_and_format_data(
    dataset, years=None, realizations=None, downscaled_raw_dir=None
):
    kwargs_all = DATASETS[dataset]
    subset_all = kwargs_all["subset"]
    if years is None:
        years = subset_all["years"]
    if realizations is None:
        realizations = subset_all["realizations"]
    years = np.atleast_1d(years)
    realizations = np.atleast_1d(realizations)
    if "downscaled" in dataset and downscaled_raw_dir is None:
        raise ValueError(
            f"downscaled_raw_dir must be provided for downscaled dataset {dataset}, "
            "which is formatted from raw files rather than downloaded."
        )

    download_confirmation_dir = (
        pathlib.Path(__file__).parents[1] / "results/downloads" / dataset
    )
    download_confirmation_dir.mkdir(parents=True, exist_ok=True)

    for year, realization in tqdm(
        itertools.product(years, realizations),
        total=len(years) * len(realizations),
    ):
        if "downscaled" in dataset:
            # Downscaled data not available for direct download
            _format_downscaled_file(
                raw_path=get_downscaled_raw_data_path(
                    dataset, realization, year, downscaled_raw_dir
                ),
                save_path=get_climate_data_path(dataset, realization, year),
                downscaled_raw_dir=downscaled_raw_dir,
                realization=realization,
                scenario=subset_all["scenarios"][0],
                year=year,
            )
        else:
            subset_current = {
                **subset_all,
                "years": [year],
                "realizations": [realization],
            }
            kwargs_current = {**kwargs_all, "subset": subset_current}
            climdata.get_climate_data(**kwargs_current)
        download_confirmation_path = (
            download_confirmation_dir / f"{realization}_{year}.txt"
        )
        with open(download_confirmation_path, "w", encoding="utf-8") as f:
            f.write("Downloaded")


def _format_downscaled_file(
    raw_path, save_path, *, downscaled_raw_dir, realization, scenario, year
):
    # The raw files are read-only source data: only ever open them, never write
    downscaled_raw_dir = pathlib.Path(downscaled_raw_dir).resolve()
    if pathlib.Path(save_path).resolve().is_relative_to(downscaled_raw_dir):
        raise ValueError(
            f"Refusing to write {save_path} inside raw data dir {downscaled_raw_dir}."
        )
    pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    ds = xr.open_dataset(raw_path, chunks={})
    ds = ds.assign_coords(
        time=xr.date_range(
            start=f"{year}-01-01", periods=365, freq="D", calendar="noleap"
        )
    )
    ds.time.encoding = {
        "dtype": "int64",
        "units": "days since 2000-01-01",
        "calendar": "noleap",
    }
    ds = ds.rename({"latitude": "lat", "longitude": "lon"})
    ds = ds.bounds.add_missing_bounds()
    ds = ds.assign(temperature=(ds["VAR_2T"] - 273.15)).drop_vars("VAR_2T")
    ds["temperature"] = (
        ds["temperature"]
        .expand_dims(realization=[realization], scenario=[scenario])
        .assign_attrs(units="degrees_Celsius")
    )
    ds.to_netcdf(save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download climate data (downscaled data is instead formatted "
        "from raw files)"
    )
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name")
    parser.add_argument(
        "--years", type=int, nargs="+", default=None, help="Years to download or format"
    )
    parser.add_argument(
        "--realizations",
        type=int,
        nargs="+",
        default=None,
        help="Realizations to download or format",
    )
    parser.add_argument(
        "--downscaled-raw-dir",
        type=str,
        default=None,
        help="Root directory of the raw downscaled data (downscaled datasets only)",
    )

    args = parser.parse_args()

    _download_and_format_data(
        dataset=args.dataset,
        years=args.years,
        realizations=args.realizations,
        downscaled_raw_dir=args.downscaled_raw_dir,
    )
