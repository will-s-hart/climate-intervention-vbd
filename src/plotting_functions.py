import pathlib
import tempfile
import unicodedata
import warnings

import climepi  # noqa
import geoviews.feature as gf
import holoviews as hv
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import numpy as np
import pandas as pd
import xarray as xr
from bokeh.io import curdoc
from bokeh.io.export import get_layout_html, wait_until_render_complete
from bokeh.models import ColorBar
from climepi._xcdat import BoundsAccessor, swap_lon_axis  # noqa
from holoviews import opts
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

WEBDRIVER_SERVICE = FirefoxService(GeckoDriverManager().install())
WEBDRIVER_OPTIONS = FirefoxOptions()
WEBDRIVER_OPTIONS.add_argument("--headless")

# Bokeh passes ColorBar.title_text_align to the colour bar's internal title as
# text_align, which titles ignore (https://github.com/bokeh/bokeh/issues/14149), so
# pass it on as align before exporting. Bokeh 4 adds colour bar title alignment options
# (https://github.com/bokeh/bokeh/pull/14152), which should make this workaround
# removable in favour of export_svg.
EXPORT_SVG_SCRIPT = """
let n_aligned = 0
for (const view of Bokeh.index.query((view) => view.model.type == "ColorBar")) {
  for (const child of view.children()) {
    if (child.model.type == "Title") {
      child.model.align = view.model.title_text_align
      n_aligned++
    }
  }
}
const [root_view] = Bokeh.index
return [n_aligned, root_view.export("svg").ctx.get_serialized_svg(true)]
"""


def make_current_plot(
    data_path=None,
    panel_label="A",
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {
        **_get_plot_opts(map_plot=True, title_offset=-90),
        "colorbar_position": "left",
    }
    plot_opts["backend_opts"]["plot.min_border_left"] = 0
    ds = xr.open_dataset(data_path)
    before_year_range = ds.attrs["before_year_range"]
    p = _make_map_plot(
        ds,
        plot_var="before",
        **{
            "title": f"{panel_label}. Dengue suitability ({before_year_range})",
            "clabel": "Mean days suitable",
            **plot_kwargs,
        },
    )
    p = p.opts(opts.Image(**plot_opts), clone=True)
    # Plot (thinned) occurrence data from https://doi.org/10.1038/s41467-025-58609-5
    df = pd.read_csv(pathlib.Path(__file__).parents[1] / "data/arbo_occ_thinned.csv")
    df = df[df["disease"] == "dengue"]
    p *= df.hvplot.points(x="Longitude", y="Latitude", color="red", size=0.5)
    save_path = f"{save_base_path}.svg"
    _save_fig(p, save_path=save_path)
    return p


def make_temperature_time_series_plot(
    data_path=None,
    panel_label="A",
    save_base_path=None,
    **plot_kwargs,
):
    colors = hv.Cycle().values
    plot_opts = {
        **_get_plot_opts(title_offset=-90),
        "xlim": (2015, 2065),
        "ylim": (14, 17),
        "xlabel": "Year",
        "ylabel": "Temperature (°C)",
        "legend_position": "top_left",
        "title": f"{panel_label}. Global mean temperature under climate change and "
        "intervention",
    }
    ds = xr.open_dataset(data_path)
    ds = ds.sel(scenario=["ssp245", "sai15"]).assign_coords(
        scenario=[
            "Without climate intervention (SSP2-4.5)",
            "With intervention (ARISE-SAI-1.5)",
        ]
    )
    ds["time"] = ds.time.dt.year
    ds_mean = ds.mean(dim="realization")
    p = (
        ds.climepi.plot_time_series(
            **{
                "by": ["scenario", "realization"],
                "color": [colors[0], colors[1]],
                "line_width": 0.5,
                "legend": False,
                **plot_kwargs,
            },
        )
        * ds_mean.climepi.plot_time_series(
            **{
                "by": "scenario",
                "color": [colors[0], colors[1]],
                **plot_kwargs,
            },
        )
        * hv.VLine(ds.time.values[20]).opts(
            line_color="black", line_dash="dashed", clone=True
        )
    )
    p = p.opts(**plot_opts, clone=True)
    save_path = f"{save_base_path}.svg"
    _save_fig(p, save_path=save_path)


def make_mean_plots(
    data_path=None,
    panel_labels=("A", "B", "C", "D"),
    save_base_path=None,
    clim_diff=None,
    **plot_kwargs,
):
    plot_opts = _get_plot_opts(map_plot=True)
    ds = xr.open_dataset(data_path)
    before_year_range = ds.attrs["before_year_range"]
    after_year_range = ds.attrs["after_year_range"]
    max_diff_before_to_after_mean = max(
        np.abs((ds["without_intervention_minus_before"]).values).max(),
        np.abs((ds["with_intervention_minus_before"]).values).max(),
    )
    p1 = _make_map_plot(
        ds,
        plot_var="before",
        **{
            "title": f"{panel_labels[0]}. Before climate intervention ({before_year_range})",
            "clabel": "Mean days suitable",
            **plot_kwargs,
        },
    )
    p1 = p1.opts(opts.Image(**plot_opts), clone=True)
    p2 = _make_map_plot(
        ds,
        plot_var="without_intervention_minus_before",
        **{
            "symmetric": True,
            "cmap": "bwr",
            "clim": clim_diff
            or (
                -max_diff_before_to_after_mean,
                max_diff_before_to_after_mean,
            ),
            "title": f"{panel_labels[1]}. Without intervention "
            f"({after_year_range} vs {before_year_range})",
            "clabel": "Change in mean days suitable",
            **plot_kwargs,
        },
    )
    p2 = p2.opts(opts.Image(**plot_opts), clone=True)
    p3 = _make_map_plot(
        ds,
        plot_var="with_intervention_minus_before",
        **{
            "symmetric": True,
            "cmap": "bwr",
            "clim": clim_diff
            or (
                -max_diff_before_to_after_mean,
                max_diff_before_to_after_mean,
            ),
            "title": f"{panel_labels[2]}. With intervention "
            f"({after_year_range} vs {before_year_range})",
            "clabel": "Change in mean days suitable",
            **plot_kwargs,
        },
    )
    p3 = p3.opts(opts.Image(**plot_opts), clone=True)
    p4 = _make_map_plot(
        ds,
        plot_var="with_minus_without_intervention",
        **{
            "symmetric": True,
            "cmap": "bwr",
            "title": f"{panel_labels[3]}. With vs without intervention ({after_year_range})",
            "clabel": "Difference in mean days suitable",
            **({"clim": clim_diff} if clim_diff else {}),
            **plot_kwargs,
        },
    )
    p4 = p4.opts(opts.Image(**plot_opts), clone=True)
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


def make_change_example_plots(
    data_path=None,
    realizations=None,
    panel_labels=None,
    save_base_path=None,
    **plot_kwargs,
):
    plot_opts = {
        **_get_plot_opts(map_plot=True),
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
        p_curr = _make_map_plot(
            ds.sel(realization=realization),
            plot_var="mean_change",
            **{
                "title": f"{panel_label}. ID {member_id} "
                f"({after_year_range} vs {before_year_range})",
                "clim": (
                    -max_diff_before_to_after_mean,
                    max_diff_before_to_after_mean,
                ),
                **plot_kwargs,
            },
        )
        p_curr = p_curr.opts(opts.Image(**plot_opts), clone=True)
        p_ex_list.append(p_curr)
    for plot, realization in zip(p_ex_list, realizations):
        member_id = f"{realization + 1:03d}"
        save_path = f"{save_base_path}_ID_{member_id}.svg"
        _save_fig(plot, save_path=save_path)


def make_location_example_plots(
    data_path=None,
    locations=None,
    highlight_realization=None,
    panel_labels=None,
    ylim_range=None,
    save_base_path=None,
    **plot_kwargs,
):
    # With ylim_range, every panel's y-axis spans that many days so the panels share a
    # scale (see _get_shared_scale_ylim_opts); without, each starts at zero
    plot_opts = {
        **_get_plot_opts(extra_title_offset=True),
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
    p_list = []
    for location, panel_label in zip(locations, panel_labels):
        ylim_opts = (
            {"ylim": (0, None)}
            if ylim_range is None
            else _get_shared_scale_ylim_opts(ds.sel(location=location), ylim_range)
        )
        p_curr = hv.VLine(ds.time.values[0]).opts(
            line_color="black", line_dash="dashed", clone=True
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
            ).opts(
                title=f"{panel_label}. {location}",
                **ylim_opts,
                **plot_opts,
                clone=True,
            )
            if highlight:
                p_curr *= ds_before_curr.climepi.plot_time_series(
                    "before_trend", **{"line_dash": "dashed", **before_plot_kwargs}
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
        # The legend is the same in every panel, so only the first shows it
        p_curr = p_curr.opts(
            legend_position="bottom_right",
            show_legend=location == locations[0],
            clone=True,
        )
        p_list.append(p_curr)
    for plot, location in zip(p_list, locations):
        # ASCII file names (e.g. sao_paulo for São Paulo) sync safely between systems
        file_name = (
            unicodedata.normalize("NFKD", location)
            .encode("ascii", "ignore")
            .decode()
            .lower()
            .replace(" ", "_")
        )
        save_path = f"{save_base_path}_{file_name}.svg"
        _save_fig(plot, save_path=save_path)


def _get_shared_scale_ylim_opts(ds_location, ylim_range, step=30):
    # Y-axis limits spanning ylim_range days, with ticks every step days. The upper
    # limit is the lowest multiple of step above the data, but at least ylim_range, so
    # the lower limit is never negative. Data too spread out to fit is clipped below.
    data_min = min(ds_location[var].min().item() for var in ds_location.data_vars)
    data_max = max(ds_location[var].max().item() for var in ds_location.data_vars)
    upper = max(int(data_max // step + 1) * step, ylim_range)
    lower = upper - ylim_range
    if data_min < lower:
        warnings.warn(
            f"{ds_location.location.item()} data ({data_min:g} to {data_max:g} days) "
            f"does not fit a y-axis range of {ylim_range} days, so is clipped below "
            f"{lower}.",
            stacklevel=2,
        )
    return {"ylim": (lower, upper), "yticks": list(range(lower, upper + 1, step))}


def _make_map_plot(ds, plot_var, **kwargs):
    ds = ds.bounds.add_missing_bounds(axes=("X",))
    ds = swap_lon_axis(ds.reset_coords(drop=True), to=(-180, 180))
    kwargs_hvplot = {
        "x": "lon",
        "y": "lat",
        "cmap": "viridis",
        "geo": True,
        "global_extent": True,
        "rasterize": True,
        "features": ["borders", "coastline"],
        "dynamic": False,
        "project": True,
        **kwargs,
    }
    return (
        ds[plot_var].hvplot.image(**kwargs_hvplot)
        * gf.ocean(fill_color="white")
        * gf.lakes(fill_color="white")
    )


def _save_fig(plot, save_path=None):
    bokeh_plot = hv.render(plot, backend="bokeh")
    bokeh_plot.sizing_mode = None  # stops warnings about width/height not being set
    html = get_layout_html(bokeh_plot, theme=curdoc().theme)
    with (
        tempfile.TemporaryDirectory() as tmp_dir,
        Firefox(options=WEBDRIVER_OPTIONS, service=WEBDRIVER_SERVICE) as driver,
    ):
        html_path = pathlib.Path(tmp_dir) / "plot.html"
        html_path.write_text(html, encoding="utf-8")
        driver.get(html_path.as_uri())
        wait_until_render_complete(driver, timeout=5)
        n_aligned, svg = driver.execute_script(EXPORT_SVG_SCRIPT)
    if n_aligned != len(bokeh_plot.select(type=ColorBar)):
        raise RuntimeError(f"Could not align colour bar titles in {save_path}")
    pathlib.Path(save_path).write_text(svg, encoding="utf-8")


def _get_plot_opts(extra_title_offset=False, map_plot=False, title_offset=None):
    title_offset = title_offset or (-65 if extra_title_offset else -15)
    plot_opts = {
        "frame_width": 500,
        "frame_height": 250,
        "fontsize": {"title": 14, "labels": 12, "ticks": 10},
        "backend_opts": {
            "plot.min_border_left": 5 - title_offset,
            "plot.output_backend": "svg",
            "plot.background_fill_color": None,
            "plot.border_fill_color": None,
            # "plot.outline_line_color": None,
            "title.text_font_style": "normal",
            "title.offset": title_offset,
            "xaxis.axis_label_text_font_style": "normal",
            "yaxis.axis_label_text_font_style": "normal",
        },
    }
    if map_plot:
        plot_opts["colorbar_opts"] = {
            "title_text_font_style": "normal",
            "title_text_align": "center",
            "title_standoff": 10,
            "padding": 5,
        }
        plot_opts["xaxis"] = None
        plot_opts["yaxis"] = None
    return plot_opts
