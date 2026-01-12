import climepi  # noqa
import xarray as xr


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


def make_mean_plot_data(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    save_path=None,
):
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
    ds_out = xr.Dataset(
        {
            "before": ds_before_mean["portion_suitable"],
            "without_intervention_minus_before": (
                ds_control_after_mean["portion_suitable"]
                - ds_before_mean["portion_suitable"]
            ),
            "with_intervention_minus_before": (
                ds_feedback_after_mean["portion_suitable"]
                - ds_before_mean["portion_suitable"]
            ),
            "with_minus_without_intervention": (
                ds_feedback_after_mean["portion_suitable"]
                - ds_control_after_mean["portion_suitable"]
            ),
        },
        attrs={
            "before_year_range": f"{before_years.start}-{before_years.stop - 1}",
            "after_year_range": f"{after_years.start}-{after_years.stop - 1}",
        },
    )
    ds_out.to_netcdf(save_path)


def make_change_example_plot_data(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    realizations=None,
    save_path=None,
):
    if realizations is None:
        realizations = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
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
    ds_out = xr.Dataset(
        {"mean_change": ds_mean_change["portion_suitable"]},
        attrs={
            "before_year_range": f"{before_years.start}-{before_years.stop - 1}",
            "after_year_range": f"{after_years.start}-{after_years.stop - 1}",
        },
    )
    ds_out.to_netcdf(save_path)


def make_change_summary_plot_data(
    ds_control=None,
    ds_feedback=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    thresholds=None,
    save_path=None,
):
    if thresholds is None:
        thresholds = [1, 15, 30]
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
    da_increase_over_threshold = ds_mean_change["portion_suitable"] >= xr.DataArray(
        thresholds, dims="threshold", coords={"threshold": thresholds}, name="threshold"
    )
    da_percent_realizations_increasing = 100 * da_increase_over_threshold.mean(
        dim="realization"
    )
    ds_out = xr.Dataset(
        {"percent_realizations_increasing": da_percent_realizations_increasing},
        attrs={
            "before_year_range": f"{before_years.start}-{before_years.stop - 1}",
            "after_year_range": f"{after_years.start}-{after_years.stop - 1}",
        },
    )
    ds_out.to_netcdf(save_path)


def make_trend_example_plot_data(
    ds_feedback=None, after_years=range(2035, 2045), realizations=None, save_path=None
):
    if realizations is None:
        realizations = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years), realization=realizations
    ).squeeze()
    ds_after_trend = (
        ds_feedback_after.rename(realization="realization_")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(realization_="realization")
    )[["portion_suitable"]]
    ds_after_trend_change = ds_after_trend.isel(time=-1) - ds_after_trend.isel(time=0)
    ds_out = xr.Dataset(
        {"trend_change": ds_after_trend_change["portion_suitable"]},
        attrs={"after_year_range": f"{after_years.start}-{after_years.stop - 1}"},
    )
    ds_out.to_netcdf(save_path)


def make_trend_summary_plot_data(
    ds_feedback=None,
    after_years=range(2035, 2045),
    thresholds=None,
    save_path=None,
):
    if thresholds is None:
        thresholds = [1, 15, 30]
    ds_feedback_after = ds_feedback.sel(
        time=ds_feedback.time.dt.year.isin(after_years)
    ).squeeze()
    ds_after_trend = (
        ds_feedback_after.rename(realization="_realization")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(_realization="realization")
    )[["portion_suitable"]]
    ds_trend_change = ds_after_trend.isel(time=-1) - ds_after_trend.isel(time=0)
    da_increase_over_threshold = ds_trend_change["portion_suitable"] >= xr.DataArray(
        thresholds, dims="threshold", coords={"threshold": thresholds}, name="threshold"
    )
    da_percent_realizations_increasing = 100 * da_increase_over_threshold.mean(
        dim="realization"
    )
    ds_out = xr.Dataset(
        {"percent_realizations_increasing": da_percent_realizations_increasing},
        attrs={"after_year_range": f"{after_years.start}-{after_years.stop - 1}"},
    )
    ds_out.to_netcdf(save_path)


def make_location_example_plot_data(
    ds_control=None,
    ds_feedback=None,
    locations=None,
    before_years=range(2025, 2035),
    after_years=range(2035, 2045),
    save_path=None,
):
    if locations is None:
        raise ValueError("locations must be specified.")
    ds_before = (
        ds_control.sel(  # feedback realizations derived from 1st 5 control realizations
            time=ds_control.time.dt.year.isin(before_years), realization=list(range(5))
        )
        .drop_vars("member_id")
        .squeeze(drop=True)
        .climepi.sel_geo(location=locations)
    )
    ds_before = ds_before.assign(time=ds_before.time.dt.year)  # avoids plotting issues
    ds_feedback_after = (
        ds_feedback.sel(time=ds_feedback.time.dt.year.isin(after_years))
        .drop_vars("member_id")
        .squeeze(drop=True)
        .climepi.sel_geo(location=locations)
    )
    ds_feedback_after = ds_feedback_after.assign(
        time=ds_feedback_after.time.dt.year  # avoids plotting issues
    )
    ds_before_trend = (
        ds_before.rename(realization="realization_")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(realization_="realization")
    )
    ds_feedback_after_trend = (
        ds_feedback_after.rename(realization="realization_")
        .climepi.ensemble_stats(deg=1)
        .sel(stat="mean", drop=True)
        .rename(realization_="realization")
    )
    rename_coords_before = {"time": "time_before", "realization": "realization_before"}
    ds_out = xr.Dataset(
        {
            "before": ds_before["portion_suitable"].rename(**rename_coords_before),
            "before_trend": ds_before_trend["portion_suitable"].rename(
                **rename_coords_before
            ),
            "after": ds_feedback_after["portion_suitable"],
            "after_trend": ds_feedback_after_trend["portion_suitable"],
        }
    )
    ds_out.to_netcdf(save_path)
