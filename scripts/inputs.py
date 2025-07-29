import pathlib

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parents[1] / "data"

DATASETS = {
    "arise_control": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2024, 2035))
            + list(range(2035, 2045))
            + list(range(2045, 2055))
            + list(range(2055, 2065)),
            "scenarios": ["ssp245"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_control",
    },
    "arise_feedback": {
        "data_source": "arise",
        "frequency": "daily",
        "subset": {
            "years": list(range(2035, 2045))
            + list(range(2045, 2055))
            + list(range(2055, 2065)),
            "scenarios": ["sai15"],
            "realizations": list(range(10)),
        },
        "save_dir": DATA_DIR / "arise_feedback",
    },
}
EPI_MODEL_NAME = "mordecai_ae_aegypti_niche"
