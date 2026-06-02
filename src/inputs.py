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
    },
    "arise_feedback_downscaled": {
        "subset": {
            "years": list(range(2035, 2065)),
            "scenarios": ["sai15"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_feedback_downscaled",
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


def _chunks(values, chunk_size):
    return [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]
