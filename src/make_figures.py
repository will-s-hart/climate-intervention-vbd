import argparse
import pathlib

import svgutils.compose as svgc
import xarray as xr

from plotting_functions import (
    make_change_example_plots,
    make_change_summary_plots,
    make_location_example_plots,
    make_mean_plots,
    make_trend_example_plots,
    make_trend_summary_plots,
)


def make_figure_panels(downscaled=False):
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"figures/{'downscaled' if downscaled else 'native'}/panels"
    )
    save_dir.mkdir(parents=True, exist_ok=True)
    ds_control = xr.open_mfdataset(
        str(
            pathlib.Path(__file__).parents[1]
            / "results/mordecai_ae_aegypti_niche/arise_control"
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
            / "results/mordecai_ae_aegypti_niche/arise_feedback"
            f"{'_downscaled' if downscaled else ''}/*.nc"
        ),
        chunks={},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    # # Fig 1 panels
    # make_mean_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     save_base_path=save_dir / "mean",
    # )
    # # Fig 2 panels
    # make_change_example_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     realizations=[0, 5],
    #     save_base_path=save_dir / "change_example",
    # )
    make_location_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="London",
        realizations=[0],
        panel_labels=["C"],
        save_base_path=save_dir / "location_london",
    )
    # # Fig S1 panels
    # make_mean_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     after_years=range(2045, 2055),
    #     panel_labels=["", "A", "B", "C"],
    #     save_base_path=save_dir / "later_mean",
    # )
    # make_mean_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     after_years=range(2055, 2065),
    #     panel_labels=["", "D", "E", "F"],
    #     save_base_path=save_dir / "even_later_mean",
    # )
    # # Fig S2 panels
    # make_change_example_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     realizations=[1, 6, 2, 7, 3, 8, 4, 9],
    #     save_base_path=save_dir / "change_example_others",
    # )
    # Fig S3 panels
    make_location_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="New York",
        realizations=[0],
        save_base_path=save_dir / "location_new_york",
    )
    make_location_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="Rome",
        realizations=[0],
        panel_labels=["B"],
        save_base_path=save_dir / "location_rome",
    )
    make_location_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="Islamabad",
        realizations=[0],
        panel_labels=["C"],
        save_base_path=save_dir / "location_islamabad",
    )
    # Fig S4 panels
    make_location_example_plots(
        ds_control=ds_control,
        ds_feedback=ds_feedback,
        location="London",
        realizations=[1, 2, 3, 4],
        save_base_path=save_dir / "location_london_others",
    )
    # # Fig S5 panels
    # make_trend_example_plots(
    #     ds_feedback=ds_feedback,
    #     save_base_path=save_dir / "trend_example",
    # )
    # # Fig S6 panels
    # make_change_summary_plots(
    #     ds_control=ds_control,
    #     ds_feedback=ds_feedback,
    #     save_base_path=save_dir / "change_summary",
    # )
    # make_trend_summary_plots(
    #     ds_feedback=ds_feedback,
    #     save_base_path=save_dir / "trend_summary",
    # )


def compile_figures(downscaled=False):
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"figures/{'downscaled' if downscaled else 'native'}"
    )
    # Figure 1
    _combine_panels(
        panel_paths=[
            save_dir / "panels/mean_before.svg",
            save_dir / "panels/mean_without_intervention_minus_before.svg",
            save_dir / "panels/mean_with_intervention_minus_before.svg",
            save_dir / "panels/mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / "figure_1.svg",
        tiling=(2, 2),
    )
    # Figure 2
    _combine_panels(
        panel_paths=[
            save_dir / "panels/change_example_ID_001.svg",
            save_dir / "panels/change_example_ID_006.svg",
            save_dir / "panels/location_london_ID_001.svg",
        ],
        save_path=save_dir / "figure_2.svg",
        panel_height=310,
        tiling=(1, 3),
        # offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    )
    # _combine_panels(
    #     panel_paths=[
    #         save_dir / "panels/change_example_ID_001.svg",
    #         save_dir / "panels/change_example_ID_006.svg",
    #         save_dir / "panels/location_london_ID_001.svg",
    #         save_dir / "panels/location_london_ID_006.svg",
    #     ],
    #     save_path=save_dir / "figure_2.svg",
    #     panel_height=310,
    #     tiling=(2, 2),
    #     offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    # )
    # Figure S1
    _combine_panels(
        panel_paths=[
            save_dir / "panels/later_mean_without_intervention_minus_before.svg",
            save_dir / "panels/later_mean_with_intervention_minus_before.svg",
            save_dir / "panels/later_mean_with_minus_without_intervention.svg",
            save_dir / "panels/even_later_mean_without_intervention_minus_before.svg",
            save_dir / "panels/even_later_mean_with_intervention_minus_before.svg",
            save_dir / "panels/even_later_mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / "figure_S1.svg",
        tiling=(3, 2),
    )
    # Figure S2
    _combine_panels(
        panel_paths=[
            save_dir / "panels/change_example_others_ID_002.svg",
            save_dir / "panels/change_example_others_ID_007.svg",
            save_dir / "panels/change_example_others_ID_003.svg",
            save_dir / "panels/change_example_others_ID_008.svg",
            save_dir / "panels/change_example_others_ID_004.svg",
            save_dir / "panels/change_example_others_ID_009.svg",
            save_dir / "panels/change_example_others_ID_005.svg",
            save_dir / "panels/change_example_others_ID_010.svg",
        ],
        save_path=save_dir / "figure_S2.svg",
        tiling=(2, 3),
    )
    # Figure S3
    _combine_panels(
        panel_paths=[
            save_dir / "panels/location_new_york_ID_001.svg",
            save_dir / "panels/location_rome_ID_001.svg",
            save_dir / "panels/location_islamabad_ID_001.svg",
        ],
        save_path=save_dir / "figure_S3.svg",
        tiling=(1, 3),
        panel_height=330,
    )
    # Figure S4
    _combine_panels(
        panel_paths=[
            save_dir / "panels/location_london_others_ID_002.svg",
            save_dir / "panels/location_london_others_ID_003.svg",
            save_dir / "panels/location_london_others_ID_004.svg",
            save_dir / "panels/location_london_others_ID_005.svg",
        ],
        save_path=save_dir / "figure_S4.svg",
        tiling=(2, 2),
        panel_height=330,
    )
    # Figure S5
    _combine_panels(
        panel_paths=[
            save_dir / "panels/trend_example_ID_001.svg",
            save_dir / "panels/trend_example_ID_006.svg",
            save_dir / "panels/trend_example_ID_002.svg",
            save_dir / "panels/trend_example_ID_007.svg",
            save_dir / "panels/trend_example_ID_003.svg",
            save_dir / "panels/trend_example_ID_008.svg",
            save_dir / "panels/trend_example_ID_004.svg",
            save_dir / "panels/trend_example_ID_009.svg",
            save_dir / "panels/trend_example_ID_005.svg",
            save_dir / "panels/trend_example_ID_010.svg",
        ],
        save_path=save_dir / "figure_S5.svg",
        tiling=(2, 5),
    )
    # Figure S6
    _combine_panels(
        panel_paths=[
            save_dir / "panels/change_summary_threshold_0.svg",
            save_dir / "panels/change_summary_threshold_15.svg",
            save_dir / "panels/change_summary_threshold_30.svg",
            save_dir / "panels/trend_summary_threshold_0.svg",
            save_dir / "panels/trend_summary_threshold_15.svg",
            save_dir / "panels/trend_summary_threshold_30.svg",
        ],
        save_path=save_dir / "figure_S6.svg",
        tiling=(3, 2),
    )


def _combine_panels(
    panel_paths, save_path, panel_width=620, panel_height=285, tiling=None, offsets=None
):
    if tiling is None:
        tiling = (len(panel_paths), 1)
    if offsets is None:
        offsets = [(0, 0)] * len(panel_paths)
    svgc.Figure(
        f"{panel_width * tiling[0]}",
        f"{panel_height * tiling[1]}",
        *[svgc.SVG(path).move(*offset) for path, offset in zip(panel_paths, offsets)],
    ).tile(*tiling).save(save_path)


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
    make_figure_panels(downscaled=args.downscaled)
    compile_figures(downscaled=args.downscaled)
