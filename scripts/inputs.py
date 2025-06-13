import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parents[1] / "data"
CDG_API_TOKEN = os.getenv("CDG_API_TOKEN")

DATASETS = {
    "arise_control": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2020, 2030)) + list(range(2060, 2070)),
            "scenarios": ["ssp245"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_control",
    },
    "arise_feedback": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2060, 2070)),
            "scenarios": ["sai15"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_feedback",
    },
    "glens_control": {
        "data_source": "glens",
        "frequency": "daily",
        "subset": {
            "years": list(range(2020, 2030))
            + list(range(2060, 2070))
            + list(range(2080, 2090)),
            "scenarios": ["rcp85"],
            "realizations": list(range(3)),
        },
        "save_dir": DATA_DIR / "glens_control",
        "api_token": CDG_API_TOKEN,
        "full_download": True,
    },
    "glens_feedback": {
        "data_source": "glens",
        "frequency": "daily",
        "subset": {
            "years": list(range(2020, 2030))
            + list(range(2060, 2070))
            + list(range(2080, 2090)),
            "scenarios": ["sai"],
            "realizations": list(range(20)),
        },
        "save_dir": DATA_DIR / "glens_feedback",
        "api_token": CDG_API_TOKEN,
        "full_download": True,
    },
}

EPI_MODEL_NAME = "mordecai_ae_aegypti_niche"
