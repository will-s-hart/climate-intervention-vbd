import argparse
import pathlib

import svgutils.compose as svgc

from inputs import ALT_EPI_MODEL_NAME, EPI_MODEL_NAME
from plotting_functions import (
    make_change_example_plots,
    make_current_plot,
    make_location_example_plots,
    make_mean_plots,
    make_temperature_time_series_plot,
)


def make_common_panels(downscaled=False, epi_model_name=None):
    # Panels shown for both epi models
    if epi_model_name is None:
        raise ValueError("epi_model_name must be provided.")
    data_dir = _get_data_dir(downscaled=downscaled, epi_model_name=epi_model_name)
    panel_dir = _get_panel_dir(downscaled=downscaled, epi_model_name=epi_model_name)
    print(f"Making mean panels for {epi_model_name}...")
    make_mean_plots(
        data_path=data_dir / "mean.nc",
        save_base_path=panel_dir / "mean",
        clim_diff=(-30, 30),
    )
    print(f"Making change example panels for {epi_model_name}...")
    make_change_example_plots(
        data_path=data_dir / "change_example.nc",
        save_base_path=panel_dir / "change_example",
        clim=(-30, 30),
    )
    print(f"Making location example panels for {epi_model_name}...")
    make_location_example_plots(
        data_path=data_dir / "location.nc",
        highlight_realization=0,
        save_base_path=panel_dir / "location",
    )


def make_primary_panels(downscaled=False):
    # Panels shown only for the primary epi model, plus the model-independent
    # temperature time series
    data_dir = _get_data_dir(downscaled=downscaled, epi_model_name=EPI_MODEL_NAME)
    panel_dir = _get_panel_dir(downscaled=downscaled, epi_model_name=EPI_MODEL_NAME)
    print("Making temperature time series panel...")
    make_temperature_time_series_plot(
        data_path=data_dir.parent / "temperature_time_series.nc",
        save_base_path=panel_dir.parent / "temperature_time_series",
    )
    print("Making current suitability panel...")
    make_current_plot(
        data_path=data_dir / "current.nc",
        panel_label="B",
        save_base_path=panel_dir / "current",
    )
    print("Making later mean panels...")
    make_mean_plots(
        data_path=data_dir / "later_mean.nc",
        panel_labels=["", "A", "C", "E"],
        save_base_path=panel_dir / "later_mean",
        clim_diff=(-50, 50),
    )
    make_mean_plots(
        data_path=data_dir / "even_later_mean.nc",
        panel_labels=["", "B", "D", "F"],
        save_base_path=panel_dir / "even_later_mean",
        clim_diff=(-80, 80),
    )
    print("Making change example (other realizations) panels...")
    make_change_example_plots(
        data_path=data_dir / "change_example_others.nc",
        save_base_path=panel_dir / "change_example_others",
        panel_labels=["A", "C", "E", "B", "D", "F"],
        clim=(-30, 30),
    )
    print("Making location example (other locations) panels...")
    make_location_example_plots(
        data_path=data_dir / "location_others.nc",
        highlight_realization=0,
        save_base_path=panel_dir / "location_others",
    )


def compile_common_figures(
    downscaled=False,
    epi_model_name=None,
    *,
    mean_figure_number,
    change_example_figure_number,
    location_figure_number,
):
    if epi_model_name is None:
        raise ValueError("epi_model_name must be provided.")
    save_dir = _get_figure_dir(downscaled=downscaled)
    panel_dir = _get_panel_dir(downscaled=downscaled, epi_model_name=epi_model_name)
    # Mean maps
    _combine_panels(
        panel_paths=[
            panel_dir / "mean_before.svg",
            panel_dir / "mean_without_intervention_minus_before.svg",
            panel_dir / "mean_with_intervention_minus_before.svg",
            panel_dir / "mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / f"figure_{mean_figure_number}.svg",
        tiling=(2, 2),
    )
    # Change example maps
    _combine_panels(
        panel_paths=[
            panel_dir / "change_example_ID_001.svg",
            panel_dir / "change_example_ID_002.svg",
            panel_dir / "change_example_ID_006.svg",
            panel_dir / "change_example_ID_007.svg",
        ],
        save_path=save_dir / f"figure_{change_example_figure_number}.svg",
        tiling=(2, 2),
        # panel_height=310,
        # offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    )
    # Location time series
    _combine_panels(
        panel_paths=[
            panel_dir / "location_london.svg",
            panel_dir / "location_seattle.svg",
            panel_dir / "location_cape_town.svg",
            panel_dir / "location_santiago_de_chile.svg",
        ],
        save_path=save_dir / f"figure_{location_figure_number}.svg",
        panel_width=580,
        panel_height=330,
        tiling=(2, 2),
        # offsets=[(0, 0), (0, 0), (0, -25), (0, -25)],
    )


def compile_primary_figures(
    downscaled=False,
    *,
    current_figure_number,
    later_mean_figure_number,
    change_example_others_figure_number,
    location_others_figure_number,
):
    save_dir = _get_figure_dir(downscaled=downscaled)
    panel_dir = _get_panel_dir(downscaled=downscaled, epi_model_name=EPI_MODEL_NAME)
    # Temperature time series and current suitability
    _combine_panels(
        panel_paths=[
            panel_dir.parent / "temperature_time_series.svg",
            panel_dir / "current.svg",
        ],
        save_path=save_dir / f"figure_{current_figure_number}.svg",
        tiling=(1, 2),
        panel_height=310,
        offsets=[(0, 0), (0, 15)],
    )
    # Later mean maps
    _combine_panels(
        panel_paths=[
            panel_dir / "later_mean_without_intervention_minus_before.svg",
            panel_dir / "even_later_mean_without_intervention_minus_before.svg",
            panel_dir / "later_mean_with_intervention_minus_before.svg",
            panel_dir / "even_later_mean_with_intervention_minus_before.svg",
            panel_dir / "later_mean_with_minus_without_intervention.svg",
            panel_dir / "even_later_mean_with_minus_without_intervention.svg",
        ],
        save_path=save_dir / f"figure_{later_mean_figure_number}.svg",
        tiling=(2, 3),
    )
    # Change example maps for the other realizations
    _combine_panels(
        panel_paths=[
            panel_dir / "change_example_others_ID_003.svg",
            panel_dir / "change_example_others_ID_008.svg",
            panel_dir / "change_example_others_ID_004.svg",
            panel_dir / "change_example_others_ID_009.svg",
            panel_dir / "change_example_others_ID_005.svg",
            panel_dir / "change_example_others_ID_010.svg",
        ],
        save_path=save_dir / f"figure_{change_example_others_figure_number}.svg",
        tiling=(2, 3),
    )
    # Location time series for the other locations
    _combine_panels(
        panel_paths=[
            panel_dir / "location_others_paris.svg",
            panel_dir / "location_others_los_angeles.svg",
            panel_dir / "location_others_addis_ababa.svg",
            panel_dir / "location_others_new_delhi.svg",
            panel_dir / "location_others_hanoi.svg",
            panel_dir / "location_others_tokyo.svg",
        ],
        save_path=save_dir / f"figure_{location_others_figure_number}.svg",
        tiling=(2, 3),
        panel_height=330,
        panel_width=580,
    )


def _get_data_dir(downscaled=False, epi_model_name=None):
    data_dir = (
        pathlib.Path(__file__).parents[1]
        / f"results/figure_data/{'downscaled' if downscaled else 'native'}"
    )
    if epi_model_name is not None:
        data_dir = data_dir / epi_model_name
    return data_dir


def _get_panel_dir(downscaled=False, epi_model_name=None):
    panel_dir = _get_figure_dir(downscaled=downscaled) / "panels"
    if epi_model_name is not None:
        panel_dir = panel_dir / epi_model_name
    panel_dir.mkdir(parents=True, exist_ok=True)
    return panel_dir


def _get_figure_dir(downscaled=False):
    return (
        pathlib.Path(__file__).parents[1]
        / f"figures/{'downscaled' if downscaled else 'native'}"
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
        make_primary_panels(downscaled=args.downscaled)
        make_common_panels(downscaled=args.downscaled, epi_model_name=EPI_MODEL_NAME)
        make_common_panels(
            downscaled=args.downscaled, epi_model_name=ALT_EPI_MODEL_NAME
        )
    print("Compiling figures...")
    compile_primary_figures(
        downscaled=args.downscaled,
        current_figure_number=1,
        later_mean_figure_number="S1",
        change_example_others_figure_number="S2",
        location_others_figure_number="S3",
    )
    compile_common_figures(
        downscaled=args.downscaled,
        epi_model_name=EPI_MODEL_NAME,
        mean_figure_number=2,
        change_example_figure_number=3,
        location_figure_number=4,
    )
    compile_common_figures(
        downscaled=args.downscaled,
        epi_model_name=ALT_EPI_MODEL_NAME,
        mean_figure_number="S4",
        change_example_figure_number="S5",
        location_figure_number="S6",
    )
