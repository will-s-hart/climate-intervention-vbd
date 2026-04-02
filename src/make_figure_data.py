import argparse
import pathlib

import xarray as xr

from figure_data_functions import (
    make_change_example_plot_data,
    make_change_summary_plot_data,
    make_location_example_plot_data,
    make_mean_plot_data,
    make_temperature_time_series_plot_data,
)


def _make_temperature_figure_data(downscaled=False):
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"results/figure_data/{'downscaled' if downscaled else 'native'}"
    )
    save_dir.mkdir(parents=True, exist_ok=True)
    ds_control_mean_temperatures = xr.open_mfdataset(
        str(
            pathlib.Path(__file__).parents[1] / "results/mean_temperatures/"
            f"arise_control{'_downscaled' if downscaled else ''}/*.nc"
        ),
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    ds_feedback_mean_temperatures = xr.open_mfdataset(
        str(
            pathlib.Path(__file__).parents[1] / "results/mean_temperatures/"
            f"arise_feedback{'_downscaled' if downscaled else ''}/*.nc"
        ),
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    make_temperature_time_series_plot_data(
        ds_control_mean_temperatures=ds_control_mean_temperatures,
        ds_feedback_mean_temperatures=ds_feedback_mean_temperatures,
        save_path=save_dir / "temperature_time_series.nc",
    )


def _make_figure_data(downscaled=False, epi_model_name=None):
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"results/figure_data/{'downscaled' if downscaled else 'native'}/"
        f"{epi_model_name}"
    )
    save_dir.mkdir(parents=True, exist_ok=True)
    ds_control = xr.open_mfdataset(
        str(
            pathlib.Path(__file__).parents[1]
            / f"results/{epi_model_name}/arise_control"
            f"{'_downscaled' if downscaled else ''}/*.nc"
        ),
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    ds_feedback = xr.open_mfdataset(
        str(
            pathlib.Path(__file__).parents[1]
            / f"results/{epi_model_name}/arise_feedback"
            f"{'_downscaled' if downscaled else ''}/*.nc"
        ),
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    # Fig 1 data
    print("Making Fig 1 data...")
    make_mean_plot_data(
        ds_control=ds_control,
        ds_feedback=None,
        before_years=range(2015, 2025),
        after_years=None,
        save_path=save_dir / "current.nc",
    )
    # Fig 2 data
    print("Making Fig 2 data...")
    make_mean_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "mean.nc",
    )
    # Fig 3 data
    print("Making Fig 3 data...")
    make_change_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        realizations=[0, 1, 5, 6],
        save_path=save_dir / "change_example.nc",
    )
    # Fig 4 data
    print("Making Fig 4 data...")
    make_location_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        locations=["London", "Seattle", "Cape Town", "Santiago de Chile"],
        save_path=save_dir / "location.nc",
    )
    # Fig S1 data
    print("Making Fig S1 data...")
    make_mean_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        after_years=range(2045, 2055),
        save_path=save_dir / "later_mean.nc",
    )
    make_mean_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        after_years=range(2055, 2065),
        save_path=save_dir / "even_later_mean.nc",
    )
    # Fig S2 data
    print("Making Fig S2 data...")
    make_change_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        realizations=[2, 3, 4, 7, 8, 9],
        save_path=save_dir / "change_example_others.nc",
    )
    # Fig S3 data
    print("Making Fig S3 data...")
    make_location_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        locations=[
            "Paris",
            "Los Angeles",
            "Addis Ababa",
            "New Delhi",
            "Hanoi",
            "Tokyo",
        ],
        save_path=save_dir / "location_others.nc",
    )
    # Fig S4 data
    print("Making Fig S4 data...")
    make_change_summary_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        thresholds=[1, 15],
        save_path=save_dir / "change_summary.nc",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate figures comparing intervention and control scenarios."
    )
    parser.add_argument(
        "--downscaled",
        action="store_true",
        help="Whether to generate figure data for downscaled climate data.",
    )
    parser.add_argument(
        "--temperature",
        action="store_true",
        help="Whether to generate data for temperature-related figures (non epi).",
    )
    parser.add_argument(
        "--epi-model-name",
        type=str,
        default=None,
        help="Epi model name to run",
    )
    args = parser.parse_args()
    if args.temperature:
        _make_temperature_figure_data(downscaled=args.downscaled)
    if args.epi_model_name:
        _make_figure_data(
            downscaled=args.downscaled, epi_model_name=args.epi_model_name
        )
    elif not args.temperature:
        raise ValueError(
            "epi_model_name must be provided to generate epi-related figure data."
        )
