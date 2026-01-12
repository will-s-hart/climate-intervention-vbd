import pathlib

DATA_DIR = pathlib.Path(__file__).parents[1] / "data"

DATASETS = {
    "arise_control": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2025, 2065)),
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
            "years": list(range(2025, 2065)),
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
