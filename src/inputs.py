import itertools
import pathlib

DATA_DIR = pathlib.Path(__file__).parents[1] / "data"

DATASETS = {
    "arise_control": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2015, 2065)),
            "scenarios": ["ssp245"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_control",
    },
    "arise_feedback": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2035, 2065)),
            "scenarios": ["sai15"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_feedback",
    },
    "arise_control_downscaled": {
        "subset": {
            "years": list(range(2015, 2065)),
            "scenarios": ["ssp245"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_control_downscaled",
        # Format spec, relative to the raw data root (config key downscaled_raw_dir)
        "raw_path_template": (
            "SSP245/bc_TREFHT_SSP245_ens{ensemble_member:03d}_{year}.nc"
        ),
    },
    "arise_feedback_downscaled": {
        "subset": {
            "years": list(range(2035, 2065)),
            "scenarios": ["sai15"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_feedback_downscaled",
        "raw_path_template": (
            "ARISE-1.5K/bc_TREFHT_SSP245_MERGED_ARISE_1.5_ens{ensemble_member:03d}_"
            "{year}.nc"
        ),
    },
}

EPI_MODEL_NAME = "mordecai_ae_aegypti_niche"
ALT_EPI_MODEL_NAME = "mordecai_ae_albopictus_niche"

YEARS_PER_JOB = 10
REALIZATIONS_PER_JOB = 1


def get_batches(dataset):
    """Partition a dataset's realizations x years grid into per-job chunks.

    Returns an ordered list of {"realizations": [...], "years": [...]} dicts;
    the Snakefile uses each chunk's position as its batch index.
    """
    subset = DATASETS[dataset]["subset"]
    realization_chunks = _chunks(subset["realizations"], REALIZATIONS_PER_JOB)
    year_chunks = _chunks(subset["years"], YEARS_PER_JOB)
    return [
        {"realizations": realization_chunk, "years": year_chunk}
        for realization_chunk, year_chunk in itertools.product(
            realization_chunks, year_chunks
        )
    ]


def get_climate_data_path(dataset, realization, year):
    """Path to the climate data for a single realization and year.

    Native files are named by climepi, so are found by globbing; downscaled files
    are written under exactly this name when the raw data is formatted.
    """
    data_dir = DATASETS[dataset]["save_dir"]
    if "downscaled" in dataset:
        return data_dir / f"{dataset}_{realization}_{year}.nc"
    (path,) = data_dir.glob(f"*_{year}_*_{realization}.nc")
    return path


def get_downscaled_raw_data_path(dataset, realization, year, downscaled_raw_dir):
    """Path to the raw file a downscaled dataset is formatted from.

    downscaled_raw_dir is the root of the (not publicly available) raw downscaled
    data; the dataset's "raw_path_template" gives the path beneath it.
    """
    # Raw ensemble members are numbered from 1, realizations from 0
    raw_path_template = DATASETS[dataset]["raw_path_template"]
    return pathlib.Path(downscaled_raw_dir) / raw_path_template.format(
        ensemble_member=realization + 1, year=year
    )


def _chunks(values, chunk_size):
    return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]
