import climepi  # noqa
import holoviews as hv
import numpy as np
import xarray as xr
from bokeh.io import export_svg
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

WEBDRIVER_SERVICE = FirefoxService(GeckoDriverManager().install())
WEBDRIVER_OPTIONS = FirefoxOptions()
WEBDRIVER_OPTIONS.add_argument("--headless")

PLOT_OPTS = {
    "frame_width": 500,
    "frame_height": 250,
    "fontsize": {"title": 14, "labels": 12, "ticks": 10},
    "backend_opts": {
        "plot.min_border_left": 20,
        "plot.output_backend": "svg",
        "plot.background_fill_color": None,
        "plot.border_fill_color": None,
        "title.text_font_style": "normal",
        "title.offset": -15,
        "xaxis.axis_label_text_font_style": "normal",
        "yaxis.axis_label_text_font_style": "normal",
    },
}
PLOT_OPTS_EXTRA_TITLE_OFFSET = {
    **PLOT_OPTS,
    "backend_opts": {
        **PLOT_OPTS["backend_opts"],
        "plot.min_border_left": 75,
        "title.offset": -70,
    },
}
MAP_PLOT_OPTS = {
    "colorbar_opts": {
        "title_text_font_style": "normal",
        "title_standoff": 10,
        "padding": 5,
    },
    "xaxis": None,
    "yaxis": None,
}


def _get_feedback_matched_before_dataset(ds_before):
    # Create a dataset where the first 5 realizations are duplicated to match the
    # realizations in the feedback dataset
    return xr.concat(
        [
            ds_before.sel(realization=[0, 1, 2, 3, 4]),
            ds_before.sel(realization=[0, 1, 2, 3, 4]).assign_coords(
                realization=[5, 6, 7, 8, 9]
            ),
        ],
        dim="realization",
        data_vars="minimal",
    )


def make_mean_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    panel_labels=("A", "B", "C", "D"),
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {**PLOT_OPTS, **MAP_PLOT_OPTS}
    ds_before = ds_control.sel(
        time=ds_control.time.dt.year.isin(before_years)
    ).squeeze()
    ds_before_mean = ds_before[["portion_suitable"]].mean(dim=["time", "realization"])
    ds_control_after = ds_control.sel(
        time=ds_control.time.dt.year.isin(after_years)
    ).squeeze()
    ds_control_after_mean = ds_control_after[["portion_suitable"]].mean(
        dim=["time", "realization"]
    )
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_feedback_after_mean = ds_feedback_after[["portion_suitable"]].mean(
        dim=["time", "realization"]
    )
    max_diff_before_to_after_mean = max(
        np.abs(
            (
                ds_control_after_mean["portion_suitable"]
                - ds_before_mean["portion_suitable"]
            ).values
        ).max(),
        np.abs(
            (
                ds_feedback_after_mean["portion_suitable"]
                - ds_before_mean["portion_suitable"]
            ).values
        ).max(),
    )
    p1 = ds_before_mean.climepi.plot_map(
        title=f"{panel_labels[0]}. Before climate intervention "
        f"({before_years.start}-{before_years.stop - 1})",
        clabel="Mean days suitable",
    )
    p1.Image.I.opts(**plot_opts)
    p2 = (ds_control_after_mean - ds_before_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"{panel_labels[1]}. Without intervention "
        f"({after_years.start}-{after_years.stop - 1} "
        f"vs {before_years.start}-{before_years.stop - 1})",
        clabel="Change in mean days suitable",
        **plot_kwargs,
    )
    p2.Image.I.opts(**plot_opts)
    p3 = (ds_feedback_after_mean - ds_before_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"{panel_labels[2]}. With intervention "
        f"({after_years.start}-{after_years.stop - 1} "
        f"vs {before_years.start}-{before_years.stop - 1})",
        clabel="Change in mean days suitable",
        **plot_kwargs,
    )
    p3.Image.I.opts(**plot_opts)
    p4 = (ds_feedback_after_mean - ds_control_after_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        title=f"{panel_labels[3]}. With vs without intervention "
        f"({after_years.start}-{after_years.stop - 1})",
        clabel="Difference in mean days suitable",
        **plot_kwargs,
    )
    p4.Image.I.opts(**plot_opts)
    plots = hv.Layout([p1, p2, p3, p4]).opts(shared_axes=False).cols(2)
    if save_base_path:
        for plot, name in zip(
            [p1, p2, p3, p4],
            [
                "before",
                "without_intervention_minus_before",
                "with_intervention_minus_before",
                "with_minus_without_intervention",
            ],
        ):
            save_path = f"{save_base_path}_{name}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def make_change_example_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    realizations=(0, 5, 1, 6, 2, 7, 3, 8, 4, 9),
    panel_labels=None,
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {
        **PLOT_OPTS,
        **MAP_PLOT_OPTS,
        "symmetric": True,
        "cmap": "bwr",
        "clabel": "Change in mean days suitable",
    }
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(realizations)]
    ds_before_feedback_matched = (
        _get_feedback_matched_before_dataset(
            ds_control.sel(time=ds_control.time.dt.year.isin(before_years))
        )
        .sel(realization=realizations)
        .squeeze()
    )
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years), realization=realizations
    ).squeeze()
    ds_mean_change = ds_feedback_after[["portion_suitable"]].mean(
        dim="time"
    ) - ds_before_feedback_matched[["portion_suitable"]].mean(dim="time")
    max_diff_before_to_after_mean = np.abs(
        ds_mean_change["portion_suitable"].values
    ).max()
    p_ex_list = []
    for realization, panel_label in zip(realizations, panel_labels):
        member_id = f"{realization + 1:03d}"
        p_curr = ds_mean_change.sel(realization=realization).climepi.plot_map(
            title=f"{panel_label}. ID {member_id} "
            f"({after_years.start}-{after_years.stop - 1} vs "
            f"{before_years.start}-{before_years.stop - 1})",
            clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
            **plot_kwargs,
        )
        p_curr.Image.I.opts(**plot_opts)
        p_ex_list.append(p_curr)
    plots = hv.Layout(p_ex_list).cols(3)
    if save_base_path:
        for plot, realization in zip(p_ex_list, realizations):
            member_id = f"{realization + 1:03d}"
            save_path = f"{save_base_path}_ID_{member_id}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def make_change_summary_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    thresholds=(0, 15, 30),
    panel_labels=("A", "B", "C"),
    save_base_path=None,
    **plot_kwargs,
):
    colors = [
        f"#{255:02x}{int(255 * (1 - i / 10)):02x}{int(255 * (1 - i / 10)):02x}"
        for i in range(11)
    ]
    cmap = [colors[0]] + [c for c in colors[1:-1] for _ in (0, 1)] + [colors[-1]]
    plot_opts = {
        **PLOT_OPTS,
        **MAP_PLOT_OPTS,
        "clim": (0, 100),
        "cmap": cmap,
        "cticks": list(range(0, 101, 10)),
    }
    ds_before = ds_control.sel(
        time=ds_control.time.dt.year.isin(before_years)
    ).squeeze()
    ds_before_feedback_matched = _get_feedback_matched_before_dataset(ds_before)
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_mean_change = ds_feedback_after[["portion_suitable"]].mean(
        dim="time"
    ) - ds_before_feedback_matched[["portion_suitable"]].mean(dim="time")
    p_list = []
    for threshold, panel_label in zip(thresholds, panel_labels):
        ds_increase = ds_mean_change >= threshold
        percent_increase = 100 * ds_increase.mean(dim="realization")
        p_curr = percent_increase.climepi.plot_map(
            title=f"{panel_label}. Increase in days suitable "
            f"({after_years.start}-{after_years.stop - 1} vs "
            f"{before_years.start}-{before_years.stop - 1}, {threshold} day threshold)",
            clabel="Percentage of ensemble members",
            **plot_kwargs,
        )
        p_curr.Image.I.opts(**plot_opts)
        p_list.append(p_curr)
    plots = hv.Layout(p_list).opts(shared_axes=False).cols(2)
    if save_base_path:
        for plot, name in zip(
            p_list, [f"threshold_{threshold}" for threshold in thresholds]
        ):
            save_path = f"{save_base_path}_{name}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def make_trend_example_plots(
    ds_feedback=None,
    after_years=range(2035, 2045),
    realizations=(0, 5, 1, 6, 2, 7, 3, 8, 4, 9),
    panel_labels=None,
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {
        **PLOT_OPTS,
        **MAP_PLOT_OPTS,
        "symmetric": True,
        "cmap": "bwr",
        "clabel": "Change in mean days suitable",
    }
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(realizations)]
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years), realization=realizations
    ).squeeze()
    ds_after_trend = (
        ds_feedback_after.rename(realization="_realization")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(_realization="realization")
    )[["portion_suitable"]]
    ds_after_trend_change = ds_after_trend.isel(time=-1) - ds_after_trend.isel(time=0)
    max_change = np.abs(ds_after_trend_change["portion_suitable"].values).max()
    p_ex_list = []
    for realization, panel_label in zip(realizations, panel_labels):
        member_id = f"{realization + 1:03d}"
        p_curr = ds_after_trend_change.sel(realization=realization).climepi.plot_map(
            title=f"{panel_label}. ID {member_id} "
            f"(trend change, {after_years.start}-{after_years.stop - 1})",
            clim=(-max_change, max_change),
            **plot_kwargs,
        )
        p_curr.Image.I.opts(**plot_opts)
        p_ex_list.append(p_curr)
    plots = hv.Layout(p_ex_list).cols(3)
    if save_base_path:
        for plot, realization in zip(p_ex_list, realizations):
            member_id = f"{realization + 1:03d}"
            save_path = f"{save_base_path}_ID_{member_id}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def make_trend_summary_plots(
    ds_feedback=None,
    after_years=range(2035, 2045),
    thresholds=(0, 15, 30),
    panel_labels=("A", "B", "C"),
    save_base_path=None,
    **plot_kwargs,
):
    colors = [
        f"#{255:02x}{int(255 * (1 - i / 10)):02x}{int(255 * (1 - i / 10)):02x}"
        for i in range(11)
    ]
    cmap = [colors[0]] + [c for c in colors[1:-1] for _ in (0, 1)] + [colors[-1]]
    plot_opts = {
        **PLOT_OPTS,
        **MAP_PLOT_OPTS,
        "clim": (0, 100),
        "cmap": cmap,
        "cticks": list(range(0, 101, 10)),
    }
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_after_trend = (
        ds_feedback_after.rename(realization="_realization")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(_realization="realization")
    )[["portion_suitable"]]
    p_list = []
    for threshold, panel_label in zip(thresholds, panel_labels):
        ds_after_trend_increase = (
            ds_after_trend.isel(time=-1) - ds_after_trend.isel(time=0)
        ) >= threshold
        percent_increase = 100 * ds_after_trend_increase.mean(dim="realization")
        p_curr = percent_increase.climepi.plot_map(
            title=f"{panel_label}. Increasing trend "
            f"({after_years.start}-{after_years.stop - 1}, {threshold} day threshold)",
            clabel="Percentage of ensemble members",
            **plot_kwargs,
        )
        p_curr.Image.I.opts(**plot_opts)
        p_list.append(p_curr)
    plots = hv.Layout(p_list).opts(shared_axes=False).cols(2)
    if save_base_path:
        for plot, name in zip(
            p_list, [f"threshold_{threshold}" for threshold in thresholds]
        ):
            save_path = f"{save_base_path}_{name}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def make_location_example_plots(
    ds_control=None,
    ds_feedback=None,
    location=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    realizations=(0, 1, 2, 3, 4),
    panel_labels=None,
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {
        **PLOT_OPTS_EXTRA_TITLE_OFFSET,
        "ylim": (0, None),
        "xlabel": "Year",
        "ylabel": "Days suitable for transmission",
    }
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(realizations)]
    ds_before = (
        ds_control.sel(time=ds_control.time.dt.year.isin(before_years))
        .climepi.sel_geo(location)
        .squeeze()
    )
    ds_before = ds_before.assign(time=ds_before.time.dt.year)  # avoids plotting issues
    ds_before_feedback_matched = _get_feedback_matched_before_dataset(ds_before)
    ds_feedback_after = (
        ds_feedback.sel(time=ds_feedback.time.dt.year.isin(after_years))
        .climepi.sel_geo(location)
        .squeeze()
    )
    ds_feedback_after = ds_feedback_after.assign(
        time=ds_feedback_after.time.dt.year  # avoids plotting issues
    )
    p_trend_list = []
    for realization_, panel_label in zip(realizations, panel_labels):
        p_trend_list_curr = []
        for realization in [realization_, (realization_ + 5) % 10]:
            member_id = f"{realization + 1:03d}"
            ds_before_curr = ds_before_feedback_matched.sel(realization=realization)
            ds_before_curr_trend = ds_before_curr.climepi.ensemble_stats(deg=1).sel(
                stat="mean", drop=True
            )
            ds_feedback_after_curr = ds_feedback_after.sel(realization=realization)
            ds_feedback_after_curr_trend = (
                ds_feedback_after_curr.climepi.ensemble_stats(deg=1).sel(
                    stat="mean", drop=True
                )
            )
            p_trend_list_curr.append(
                xr.concat(
                    [ds_before_curr, ds_feedback_after_curr],
                    dim="time",
                    data_vars="minimal",
                    coords="minimal",
                    compat="override",
                )
                .climepi.plot_time_series(
                    label=f"ID {member_id}",
                    color="black",
                    **plot_kwargs,
                )
                .opts(**plot_opts)
                * ds_before_curr_trend.climepi.plot_time_series(
                    color="blue", **plot_kwargs
                )
                * ds_feedback_after_curr_trend.climepi.plot_time_series(
                    color="blue", **plot_kwargs
                )
                * hv.VLine(ds_feedback_after_curr.time.values[0]).opts(
                    line_color="grey", line_dash="dashed"
                )
            )
        p_trend_list.append(
            hv.Overlay(p_trend_list_curr).opts(title=f"{panel_label}. {location}")
        )
    plots = hv.Layout(p_trend_list).opts(shared_axes=True).cols(2)
    if save_base_path:
        for plot, realization in zip(plots, realizations):
            member_id = f"{realization + 1:03d}"
            save_path = f"{save_base_path}_ID_{member_id}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def _save_fig(plot, save_path=None):
    with Firefox(options=WEBDRIVER_OPTIONS, service=WEBDRIVER_SERVICE) as driver:
        bokeh_plot = hv.render(plot, backend="bokeh")
        export_svg(bokeh_plot, filename=save_path, webdriver=driver)
