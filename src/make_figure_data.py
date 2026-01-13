import argparse
import pathlib

import xarray as xr

from figure_data_functions import (
    make_change_example_plot_data,
    make_change_summary_plot_data,
    make_location_example_plot_data,
    make_mean_plot_data,
    make_trend_example_plot_data,
    make_trend_summary_plot_data,
)


def _make_figure_data(downscaled=False, epi_model_name=None):
    if epi_model_name is None:
        raise ValueError("epi_model_name must be provided.")
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
        ds_feedback=ds_feedback,
        save_path=save_dir / "mean.nc",
    )
    # Fig 2 data
    print("Making Fig 2 data...")
    make_change_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "change_example.nc",
    )
    make_location_example_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        locations=["London"],
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
        realizations=[1, 6, 2, 7, 3, 8, 4, 9],
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
            "Santiago de Chile",
            "Addis Ababa",
            "New Delhi",
            "Hanoi",
            "Tokyo",
            "Sydney",
        ],
        save_path=save_dir / "location_others.nc",
    )
    # Fig S4 data
    print("Making Fig S4 data...")
    make_trend_example_plot_data(
        ds_feedback=ds_feedback,
        save_path=save_dir / "trend_example.nc",
    )
    # Fig S5 data
    print("Making Fig S5 data...")
    make_change_summary_plot_data(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "change_summary.nc",
    )
    make_trend_summary_plot_data(
        ds_feedback=ds_feedback,
        save_path=save_dir / "trend_summary.nc",
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
        "--epi-model-name",
        type=str,
        default=None,
        help="Epi model name to run",
    )
    args = parser.parse_args()
    _make_figure_data(downscaled=args.downscaled, epi_model_name=args.epi_model_name)
