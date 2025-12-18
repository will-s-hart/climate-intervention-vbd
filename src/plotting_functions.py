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


PLOT_KWARGS = {"frame_width": 500}


def make_mean_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    save_path=None,
    **kwargs,
):
    plot_kwargs = {**PLOT_KWARGS, **kwargs}
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
        title=f"Before intervention ({before_years.start}-{before_years.stop - 1})",
        **plot_kwargs,
    )
    p2 = (ds_control_after_mean - ds_before_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"No intervention ({after_years.start}-{after_years.stop - 1}) "
        f"minus before ({before_years.start}-{before_years.stop - 1})",
        **plot_kwargs,
    )
    p3 = (ds_feedback_after_mean - ds_before_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        clim=(-max_diff_before_to_after_mean, max_diff_before_to_after_mean),
        title=f"With intervention ({after_years.start}-{after_years.stop - 1}) "
        f"minus before ({before_years.start}-{before_years.stop - 1})",
        **plot_kwargs,
    )
    p4 = (ds_feedback_after_mean - ds_control_after_mean).climepi.plot_map(
        symmetric=True,
        cmap="bwr",
        title="With minus without intervention "
        f"({after_years.start}-{after_years.stop - 1})",
        **plot_kwargs,
    )
    plots = hv.Layout([p1, p2, p3, p4]).opts(shared_axes=False).cols(2)
    if save_path:
        _save_fig(plots, save_path=save_path)
    return plots


def make_icv_summary_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    threshold=1,
    save_path=None,
    **kwargs,
):
    plot_kwargs = {**PLOT_KWARGS, **kwargs}
    ds_before = ds_control.sel(
        time=ds_control.time.dt.year.isin(before_years)
    ).squeeze()
    ds_before_feedback_matched = xr.concat(
        [
            ds_before.isel(realization=[0, 1, 2, 3, 4]),
            ds_before.isel(realization=[0, 1, 2, 3, 4]).assign_coords(
                realization=[5, 6, 7, 8, 9]
            ),
        ],
        dim="realization",
        data_vars="minimal",
    )
    ds_control_after = ds_control.sel(
        time=ds_control.time.dt.year.isin(after_years)
    ).squeeze()
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_mean_change_control = ds_control_after[["portion_suitable"]].mean(
        dim="time"
    ) - ds_before[["portion_suitable"]].mean(dim="time")
    ds_mean_change_feedback = ds_feedback_after[["portion_suitable"]].mean(
        dim="time"
    ) - ds_before_feedback_matched[["portion_suitable"]].mean(dim="time")
    ds_sims_increased_risk_control = (ds_mean_change_control >= threshold).sum(
        dim="realization"
    )
    ds_sims_increased_risk_feedback = (ds_mean_change_feedback >= threshold).sum(
        dim="realization"
    )
    ds_uncertain_locations_feedback = (ds_sims_increased_risk_feedback > 0) * (
        ds_sims_increased_risk_feedback < 10
    )
    p1 = ds_sims_increased_risk_control.climepi.plot_map(
        # cmap="bwr",
        cmap=["blue"] + ["white"] * 8 + ["red"],
        clabel=f"Sims with >= {threshold} more mean days suitable ",
        title=f"{after_years.start}-{after_years.stop - 1} vs. "
        f"{before_years.start}-{before_years.stop - 1}, no intervention",
        **plot_kwargs,
    )
    p2 = ds_sims_increased_risk_feedback.climepi.plot_map(
        # cmap="bwr",
        cmap=["blue"] + ["white"] * 8 + ["red"],
        clabel=f"Sims with >= {threshold} more mean days suitable ",
        title=f"{after_years.start}-{after_years.stop - 1} vs. "
        f"{before_years.start}-{before_years.stop - 1}, with intervention",
        **plot_kwargs,
    )
    p3 = ds_uncertain_locations_feedback.climepi.plot_map(
        title="Locations with uncertain impact of intervention",
        cmap=["white", "red"],
        colorbar=False,
        **plot_kwargs,
    )
    plots = hv.Layout([p1, p2, p3]).opts(shared_axes=False).cols(2)
    if save_path:
        _save_fig(plots, save_path=save_path)
    return plots


def make_icv_summary_max_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    threshold=1,
    save_path=None,
    **kwargs,
):
    plot_kwargs = {**PLOT_KWARGS, **kwargs}
    ds_before = ds_control.sel(
        time=ds_control.time.dt.year.isin(before_years)
    ).squeeze()
    ds_before_feedback_matched = xr.concat(
        [
            ds_before.isel(realization=[0, 1, 2, 3, 4]),
            ds_before.isel(realization=[0, 1, 2, 3, 4]).assign_coords(
                realization=[5, 6, 7, 8, 9]
            ),
        ],
        dim="realization",
        data_vars="minimal",
    )
    ds_control_after = ds_control.sel(
        time=ds_control.time.dt.year.isin(after_years)
    ).squeeze()
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_max_change_control = ds_control_after[["portion_suitable"]].max(
        dim="time"
    ) - ds_before[["portion_suitable"]].max(dim="time")
    ds_max_change_feedback = ds_feedback_after[["portion_suitable"]].max(
        dim="time"
    ) - ds_before_feedback_matched[["portion_suitable"]].max(dim="time")
    ds_sims_increased_risk_control = (ds_max_change_control >= threshold).sum(
        dim="realization"
    )
    ds_sims_increased_risk_feedback = (ds_max_change_feedback >= threshold).sum(
        dim="realization"
    )
    ds_uncertain_locations_feedback = (ds_sims_increased_risk_feedback > 0) * (
        ds_sims_increased_risk_feedback < 10
    )
    p1 = ds_sims_increased_risk_control.climepi.plot_map(
        # cmap="bwr",
        cmap=["blue"] + ["white"] * 8 + ["red"],
        clabel=f"Sims with >= {threshold} more max days suitable ",
        title=f"{after_years.start}-{after_years.stop - 1} vs. "
        f"{before_years.start}-{before_years.stop - 1}, no intervention",
        **plot_kwargs,
    )
    p2 = ds_sims_increased_risk_feedback.climepi.plot_map(
        # cmap="bwr",
        cmap=["blue"] + ["white"] * 8 + ["red"],
        clabel=f"Sims with >= {threshold} more max days suitable ",
        title=f"{after_years.start}-{after_years.stop - 1} vs. "
        f"{before_years.start}-{before_years.stop - 1}, with intervention",
        **plot_kwargs,
    )
    p3 = ds_uncertain_locations_feedback.climepi.plot_map(
        title="Locations with uncertain impact of intervention",
        cmap=["white", "red"],
        colorbar=False,
        **plot_kwargs,
    )
    plots = hv.Layout([p1, p2, p3]).opts(shared_axes=False).cols(2)
    if save_path:
        _save_fig(plots, save_path=save_path)
    return plots


def make_example_plots(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    realizations=range(5),
    save_path=None,
    **kwargs,
):
    plot_kwargs = {
        **PLOT_KWARGS,
        "symmetric": True,
        "cmap": "bwr",
        "clabel": "Change in mean days suitable",
        **kwargs,
    }
    ds_before = ds_control.sel(
        time=ds_control.time.dt.year.isin(before_years)
    ).squeeze()
    ds_control_after = ds_control.sel(
        time=ds_control.time.dt.year.isin(after_years)
    ).squeeze()
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    p_ex_list = []
    for realization in realizations:
        if realization not in range(5):
            raise ValueError(
                "'realization' must be in range 0 to 4 (inclusive) to match first five "
                "ARISE control simulations used to initialize feedback simulations."
            )
        realization_other = realization + 5
        member_id = (
            ds_before["member_id"].isel(realization=realization).compute().item()
        )
        member_id_other = (
            ds_before["member_id"].isel(realization=realization_other).compute().item()
        )
        p_ex_list.append(
            (
                ds_control_after[["portion_suitable"]]
                .isel(realization=realization)
                .mean(dim="time")
                - ds_before[["portion_suitable"]]
                .isel(realization=realization)
                .mean(dim="time")
            ).climepi.plot_map(
                title=f"ID {member_id}, no intervention "
                f"({after_years.start}-{after_years.stop - 1} vs. "
                f"{before_years.start}-{before_years.stop - 1})",
                **plot_kwargs,
            )
        )
        p_ex_list.append(
            (
                ds_feedback_after[["portion_suitable"]]
                .isel(realization=realization)
                .mean(dim="time")
                - ds_before[["portion_suitable"]]
                .isel(realization=realization)
                .mean(dim="time")
            ).climepi.plot_map(
                title=f"ID {member_id}, with intervention "
                f"({after_years.start}-{after_years.stop - 1} vs. "
                f"{before_years.start}-{before_years.stop - 1})",
                **plot_kwargs,
            )
        )
        p_ex_list.append(
            (
                ds_feedback_after[["portion_suitable"]]
                .isel(realization=realization_other)
                .mean(dim="time")
                - ds_before[["portion_suitable"]]
                .isel(realization=realization_other)
                .mean(dim="time")
            ).climepi.plot_map(
                title=f"ID {member_id_other}, with intervention "
                f"({after_years.start}-{after_years.stop - 1} vs. "
                f"{before_years.start}-{before_years.stop - 1})",
                **plot_kwargs,
            )
        )
    plots = hv.Layout(p_ex_list).opts(shared_axes=True).cols(3)
    if save_path:
        _save_fig(plots, save_path=save_path)
    return plots


def make_trend_plots(
    ds_control=None,
    ds_feedback=None,
    location=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    realizations=None,
    save_path=None,
    **kwargs,
):
    plot_kwargs = {
        **PLOT_KWARGS,
        **kwargs,
    }
    ds_before = (
        ds_control.sel(time=ds_control.time.dt.year.isin(before_years))
        .climepi.sel_geo(location)
        .squeeze()
    )
    ds_control_after = (
        ds_control.sel(time=ds_control.time.dt.year.isin(after_years))
        .climepi.sel_geo(location)
        .squeeze()
    )
    p_trend_list = []
    realizations = realizations or ds_before.realization.values
    for realization in realizations:
        member_id = (
            ds_before["member_id"].isel(realization=realization).compute().item()
        )
        ds_before_curr = ds_before.isel(realization=realization)
        ds_before_curr_trend = ds_before_curr.climepi.ensemble_stats(deg=1).sel(
            stat="mean", drop=True
        )
        ds_control_after_curr = ds_control_after.isel(realization=realization)
        ds_control_after_curr_trend = ds_control_after_curr.climepi.ensemble_stats(
            deg=1
        ).sel(stat="mean", drop=True)
        p_trend_list.append(
            ds_before_curr.climepi.plot_time_series(
                title=f"ID {member_id}",
                color="black",
                **plot_kwargs,
            )
            * ds_before_curr_trend.climepi.plot_time_series(color="blue", **plot_kwargs)
            * ds_control_after_curr.climepi.plot_time_series(
                color="black",
                **plot_kwargs,
            )
            * ds_control_after_curr_trend.climepi.plot_time_series(
                color="blue", **plot_kwargs
            )
        )
    plots = hv.Layout(p_trend_list).opts(shared_axes=True).cols(2)
    if save_path:
        _save_fig(plots, save_path=save_path)
    return plots


def _save_fig(plots, save_path=None):
    with Firefox(options=WEBDRIVER_OPTIONS, service=WEBDRIVER_SERVICE) as driver:
        bokeh_plots = hv.render(plots, backend="bokeh")
        export_svg(bokeh_plots, filename=f"{save_path}.svg", webdriver=driver)
