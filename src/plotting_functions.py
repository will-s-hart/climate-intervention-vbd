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


def make_mean_plots(
    data_path=None,
    panel_labels=("A", "B", "C", "D"),
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {**PLOT_OPTS, **MAP_PLOT_OPTS}
    ds = xr.open_dataset(data_path)
    before_year_range = ds.attrs["before_year_range"]
    after_year_range = ds.attrs["after_year_range"]
    max_diff_before_to_after_mean = max(
        np.abs((ds["without_intervention_minus_before"]).values).max(),
        np.abs((ds["with_intervention_minus_before"]).values).max(),
    )
    p1 = ds.climepi.plot_map(
        "before",
        title=f"{panel_labels[0]}. Before climate intervention ({before_year_range})",
        clabel="Mean days suitable",
    )
    p1.Image.I.opts(**plot_opts)
    p2 = ds.climepi.plot_map(
        "without_intervention_minus_before",
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"{panel_labels[1]}. Without intervention "
        f"({after_year_range} vs {before_year_range})",
        clabel="Change in mean days suitable",
        **plot_kwargs,
    )
    p2.Image.I.opts(**plot_opts)
    p3 = ds.climepi.plot_map(
        "with_intervention_minus_before",
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"{panel_labels[2]}. With intervention "
        f"({after_year_range} vs {before_year_range})",
        clabel="Change in mean days suitable",
        **plot_kwargs,
    )
    p3.Image.I.opts(**plot_opts)
    p4 = ds.climepi.plot_map(
        "with_minus_without_intervention",
        symmetric=True,
        cmap="bwr",
        title=f"{panel_labels[3]}. With vs without intervention ({after_year_range})",
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
    data_path=None,
    realizations=None,
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
    ds = xr.open_dataset(data_path)
    if realizations is None:
        realizations = ds.realization.values.tolist()
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(realizations)]
    before_year_range = ds.attrs["before_year_range"]
    after_year_range = ds.attrs["after_year_range"]
    max_diff_before_to_after_mean = np.abs(ds["mean_change"].values).max()
    p_ex_list = []
    for realization, panel_label in zip(realizations, panel_labels):
        member_id = f"{realization + 1:03d}"
        p_curr = ds.sel(realization=realization).climepi.plot_map(
            title=f"{panel_label}. ID {member_id} "
            f"({after_year_range} vs {before_year_range})",
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
    data_path=None,
    thresholds=None,
    panel_labels=None,
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
    ds = xr.open_dataset(data_path)
    before_year_range = ds.attrs["before_year_range"]
    after_year_range = ds.attrs["after_year_range"]
    if thresholds is None:
        thresholds = ds.threshold.values.tolist()
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(thresholds)]
    p_list = []
    for threshold, panel_label in zip(thresholds, panel_labels):
        p_curr = ds.sel(threshold=threshold).climepi.plot_map(
            title=f"{panel_label}. Increase in mean days suitable "
            f"({after_year_range} vs {before_year_range}, {threshold} day threshold)",
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
    data_path=None,
    realizations=None,
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
    ds = xr.open_dataset(data_path)
    after_year_range = ds.attrs["after_year_range"]
    if realizations is None:
        realizations = ds.realization.values.tolist()
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(realizations)]
    max_change = np.abs(ds["trend_change"].values).max()
    p_ex_list = []
    for realization, panel_label in zip(realizations, panel_labels):
        member_id = f"{realization + 1:03d}"
        p_curr = ds.sel(realization=realization).climepi.plot_map(
            title=f"{panel_label}. ID {member_id} (trend change, {after_year_range})",
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
    data_path=None,
    thresholds=None,
    panel_labels=None,
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
    ds = xr.open_dataset(data_path)
    after_year_range = ds.attrs["after_year_range"]
    if thresholds is None:
        thresholds = ds.threshold.values.tolist()
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(thresholds)]
    p_list = []
    for threshold, panel_label in zip(thresholds, panel_labels):
        p_curr = ds.sel(threshold=threshold).climepi.plot_map(
            title=f"{panel_label}. Increasing trend "
            f"({after_year_range}, {threshold} day threshold)",
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
    data_path=None,
    locations=None,
    highlight_realization=None,
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
    ds = xr.open_dataset(data_path)
    ds_before = ds[["before", "before_trend"]].rename(
        time_before="time", realization_before="realization"
    )
    ds_after = ds[["after", "after_trend"]]
    if locations is None:
        locations = ds.location.values.tolist()
    if panel_labels is None:
        panel_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[: len(locations)]
    colors = hv.Cycle().values
    p_trend_list = []
    for location, panel_label in zip(locations, panel_labels):
        p_curr = hv.VLine(ds.time.values[0]).opts(
            line_color="black", line_dash="dashed"
        )
        for realization in range(5):
            realization_pair = [realization, (realization + 5) % 10]
            member_id_pair = [f"{x + 1:03d}" for x in realization_pair]
            highlight = highlight_realization in realization_pair
            before_plot_kwargs = {
                **plot_kwargs,
                "color": colors[6] if highlight else "grey",
                **({"line_width": 1, "alpha": 0.75} if not highlight else {}),
            }
            ds_before_curr = ds_before.sel(realization=realization, location=location)
            p_curr *= ds_before_curr.climepi.plot_time_series(
                "before", **before_plot_kwargs
            ).opts(title=f"{panel_label}. {location}", **plot_opts)
            if highlight:
                p_curr *= ds_before_curr.climepi.plot_time_series(
                    "before", line_dash="dashed", **before_plot_kwargs
                )
            for realization_, member_id_, color in zip(
                realization_pair,
                member_id_pair,
                ([colors[0], colors[1]] if highlight else ["grey", "grey"]),
            ):
                ds_after_curr = ds_after.sel(
                    realization=realization_, location=location
                )
                after_plot_kwargs = {
                    **plot_kwargs,
                    "color": color,
                    **(
                        {"line_width": 0.5}
                        if not highlight
                        else {"label": f"ID {member_id_}"}
                    ),
                }
                p_curr *= (
                    xr.concat(
                        [
                            ds_before_curr["before"].isel(time=-1),
                            ds_after_curr["after"],
                        ],
                        dim="time",
                        coords="minimal",
                        compat="override",
                    )
                    .to_dataset()
                    .climepi.plot_time_series(**after_plot_kwargs)
                )
                if highlight:
                    after_trend_plot_kwargs = {
                        "line_dash": "dashed",
                        **{k: v for k, v in after_plot_kwargs.items() if k != "label"},
                    }
                    p_curr *= ds_after_curr.climepi.plot_time_series(
                        "after_trend", **after_trend_plot_kwargs
                    )
        p_curr.opts(legend_position="bottom_right")
        p_trend_list.append(p_curr)
    plots = hv.Layout(p_trend_list).opts(shared_axes=True).cols(2)
    if save_base_path:
        for plot, location in zip(plots, locations):
            save_path = f"{save_base_path}_{location.lower().replace(' ', '_')}.svg"
            _save_fig(plot, save_path=save_path)
    return plots


def _save_fig(plot, save_path=None):
    with Firefox(options=WEBDRIVER_OPTIONS, service=WEBDRIVER_SERVICE) as driver:
        bokeh_plot = hv.render(plot, backend="bokeh")
        bokeh_plot.sizing_mode = None  # stops warnings about width/height not being set
        export_svg(bokeh_plot, filename=save_path, webdriver=driver)
