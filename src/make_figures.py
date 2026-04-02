import argparse
import pathlib

import svgutils.compose as svgc

from inputs import ALT_EPI_MODEL_NAME, EPI_MODEL_NAME
from plotting_functions import (
    make_change_example_plots,
    make_change_summary_plots,
    make_current_plot,
    make_location_example_plots,
    make_mean_plots,
    make_temperature_time_series_plot,
)


def make_figure_panels(downscaled=False, epi_model_name=None, main_only=False):
    if epi_model_name is None:
        raise ValueError("epi_model_name must be provided.")
    data_dir = (
        pathlib.Path(__file__).parents[1]
        / f"results/figure_data/{'downscaled' if downscaled else 'native'}/"
        f"{epi_model_name}"
    )
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"figures/{'downscaled' if downscaled else 'native'}/panels/{epi_model_name}"
    )
    save_dir.mkdir(parents=True, exist_ok=True)
    # Fig 1 panels
    print("Making Fig 1 panels...")
    make_current_plot(
        data_path=data_dir / "current.nc", save_base_path=save_dir / "current"
    )
    make_temperature_time_series_plot(
        data_path=data_dir.parent / "temperature_time_series.nc",
        save_base_path=save_dir / "temperature_time_series",
    )
    # Fig 2 panels
    print("Making Fig 2 panels...")
    make_mean_plots(data_path=data_dir / "mean.nc", save_base_path=save_dir / "mean")
    # Fig 3 panels
    print("Making Fig 3 panels...")
    make_change_example_plots(
        data_path=data_dir / "change_example.nc",
        save_base_path=save_dir / "change_example",
    )
    # Fig 4 panels
    print("Making Fig 4 panels...")
    make_location_example_plots(
        data_path=data_dir / "location.nc",
        highlight_realization=0,
        save_base_path=save_dir / "location",
    )
    if main_only:
        return
    # Fig S1 panels
    print("Making Fig S1 panels...")
    make_mean_plots(
        data_path=data_dir / "later_mean.nc",
        panel_labels=["", "A", "C", "E"],
        save_base_path=save_dir / "later_mean",
    )
    make_mean_plots(
        data_path=data_dir / "even_later_mean.nc",
        panel_labels=["", "B", "D", "F"],
        save_base_path=save_dir / "even_later_mean",
    )
    # Fig S2 panels
    print("Making Fig S2 panels...")
    make_change_example_plots(
        data_path=data_dir / "change_example_others.nc",
        save_base_path=save_dir / "change_example_others",
        panel_labels=["A", "C", "E", "B", "D", "F"],
    )
    # Fig S3 panels
    print("Making Fig S3 panels...")
    make_location_example_plots(
        data_path=data_dir / "location_others.nc",
        highlight_realization=0,
        save_base_path=save_dir / "location_others",
    )
    # Fig S4 panels
    print("Making Fig S4 panels...")
    make_change_summary_plots(
        data_path=data_dir / "change_summary.nc",
        save_base_path=save_dir / "change_summary",
    )


def compile_figures(
    downscaled=False,
    epi_model_name=EPI_MODEL_NAME,
    main_only=False,
    figure_numbers=None,
):
    save_dir = (
        pathlib.Path(__file__).parents[1]
        / f"figures/{'downscaled' if downscaled else 'native'}"
    )
    panel_dir = save_dir / "panels" / epi_model_name
    if figure_numbers is None:
        figure_numbers = [1, 2, 3, 4]
        if not main_only:
            figure_numbers += [f"S{i}" for i in range(1, 5)]
    # Figure 1
    _combine_panels(
        panel_paths=[
            panel_dir / "current.svg",
            panel_dir / "temperature_time_series.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[0]}.svg",
        tiling=(1, 2),
        panel_height=310,
        offsets=[(0, 0), (0, -25)],
    )
    # Figure 2
    _combine_panels(
        panel_paths=[
            panel_dir / "mean_before.svg",
            panel_dir / "mean_without_intervention_minus_before.svg",
            panel_dir / "mean_with_intervention_minus_before.svg",
            panel_dir / "mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[1]}.svg",
        tiling=(2, 2),
    )
    # Figure 3
    _combine_panels(
        panel_paths=[
            panel_dir / "change_example_ID_001.svg",
            panel_dir / "change_example_ID_002.svg",
            panel_dir / "change_example_ID_006.svg",
            panel_dir / "change_example_ID_007.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[2]}.svg",
        tiling=(2, 2),
        # panel_height=310,
        # offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    )
    # Figure 4
    _combine_panels(
        panel_paths=[
            panel_dir / "location_london.svg",
            panel_dir / "location_seattle.svg",
            panel_dir / "location_cape_town.svg",
            panel_dir / "location_santiago_de_chile.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[3]}.svg",
        panel_width=580,
        panel_height=330,
        tiling=(2, 2),
        # offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    )
    if main_only:
        return
    # Figure S1
    _combine_panels(
        panel_paths=[
            panel_dir / "later_mean_without_intervention_minus_before.svg",
            panel_dir / "even_later_mean_without_intervention_minus_before.svg",
            panel_dir / "later_mean_with_intervention_minus_before.svg",
            panel_dir / "even_later_mean_with_intervention_minus_before.svg",
            panel_dir / "later_mean_with_minus_without_intervention.svg",
            panel_dir / "even_later_mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[4]}.svg",
        tiling=(2, 3),
    )
    # Figure S2
    _combine_panels(
        panel_paths=[
            panel_dir / "change_example_others_ID_003.svg",
            panel_dir / "change_example_others_ID_008.svg",
            panel_dir / "change_example_others_ID_004.svg",
            panel_dir / "change_example_others_ID_009.svg",
            panel_dir / "change_example_others_ID_005.svg",
            panel_dir / "change_example_others_ID_010.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[5]}.svg",
        tiling=(2, 3),
    )
    # Figure S3
    _combine_panels(
        panel_paths=[
            panel_dir / "location_others_paris.svg",
            panel_dir / "location_others_los_angeles.svg",
            panel_dir / "location_others_addis_ababa.svg",
            panel_dir / "location_others_new_delhi.svg",
            panel_dir / "location_others_hanoi.svg",
            panel_dir / "location_others_tokyo.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[6]}.svg",
        tiling=(2, 3),
        panel_height=330,
        panel_width=580,
    )
    # Figure S4
    _combine_panels(
        panel_paths=[
            panel_dir / "change_summary_threshold_1.svg",
            panel_dir / "change_summary_threshold_15.svg",
        ],
        save_path=save_dir / f"figure_{figure_numbers[7]}.svg",
        tiling=(2, 1),
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
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Only compile figures from existing panels.",
    )
    args = parser.parse_args()
    if not args.compile_only:
        make_figure_panels(downscaled=args.downscaled, epi_model_name=EPI_MODEL_NAME)
        make_figure_panels(
            downscaled=args.downscaled,
            epi_model_name=ALT_EPI_MODEL_NAME,
            main_only=True,
        )
    print("Compiling figures...")
    compile_figures(downscaled=args.downscaled)
    compile_figures(
        downscaled=args.downscaled,
        epi_model_name=ALT_EPI_MODEL_NAME,
        main_only=True,
        figure_numbers=["S5", "S6", "S7", "S8"],
    )
