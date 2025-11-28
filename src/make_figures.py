import argparse
import pathlib

import xarray as xr

from plotting_functions import (
    make_example_plots,
    make_icv_summary_max_plots,
    make_icv_summary_plots,
    make_mean_plots,
    make_trend_plots,
)


def _make_figures(downscaled=False):
    save_dir = pathlib.Path(f"../figures/{'downscaled' if downscaled else 'native'}")
    ds_control = xr.open_mfdataset(
        f"../results/mordecai_ae_aegypti_niche/arise_control{'_downscaled_' if downscaled else '_'}/*.nc",
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    ds_feedback = xr.open_mfdataset(
        f"../results/mordecai_ae_aegypti_niche/arise_feedback{'_downscaled_' if downscaled else '_'}/*.nc",
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    make_mean_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "before_after_intervention_mean",
    )
    make_icv_summary_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "before_after_intervention_icv_summary",
    )
    make_icv_summary_max_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "before_after_intervention_icv_summary_max",
    )
    make_icv_summary_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        threshold=7,
        save_path=save_dir / "before_after_intervention_icv_summary_threshold",
    )
    make_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        save_path=save_dir / "before_after_intervention_individual_realizations",
        realizations=[0],
    )
    make_mean_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        after_years=range(2055, 2065),
        save_path=save_dir / "later_mean",
    )
    make_icv_summary_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        after_years=range(2055, 2065),
        save_path=save_dir / "later_icv_summary",
    )
    make_trend_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="London",
        realizations=[0, 1, 2, 3, 4],
        save_path=save_dir / "trend_london",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate figures comparing intervention and control scenarios."
    )
    parser.add_argument(
        "--downscaled",
        action="store_true",
        help="Whether to generate figures for downscaled data.",
    )
    args = parser.parse_args()
    _make_figures(downscaled=args.downscaled)
