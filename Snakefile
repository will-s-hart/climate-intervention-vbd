from src.inputs import DATASETS, EPI_MODEL_NAME

EPI_MODELS = [EPI_MODEL_NAME]


def get_download_file(dataset, realization, year):
    return f"results/downloads/{dataset}_{realization}_{year}.txt"


def get_result_file(dataset, realization, year, epi_model_name):
    return f"results/{dataset}_{epi_model_name}/{realization}_{year}.nc"


download_files = [
    get_download_file(dataset, realization, year)
    for dataset, meta in DATASETS.items()
    for realization in meta["subset"]["realizations"]
    for year in meta["subset"]["years"]
]

result_files = [
    get_result_file(dataset, realization, year, epi_model_name)
    for dataset, meta in DATASETS.items()
    for realization in meta["subset"]["realizations"]
    for year in meta["subset"]["years"]
    for epi_model_name in EPI_MODELS
]


rule all:
    input:
        download_files + result_files,


rule downloads:
    input:
        download_files,


rule results:
    input:
        result_files,


rule download_data:
    input:
        "src/inputs.py",
        "src/download_data.py",
    output:
        get_download_file("{dataset}", "{realization}", "{year}"),
    shell:
        """
        pixi run python src/download_data.py \
            --dataset {wildcards.dataset} \
            --years {wildcards.year} \
            --realizations {wildcards.realization}
        """


rule run_epi_model:
    input:
        lambda wildcards: get_download_file(
            wildcards.dataset, wildcards.realization, wildcards.year
        ),
        "src/inputs.py",
        "src/run_epi_model.py",
    output:
        get_result_file("{dataset}", "{realization}", "{year}", "{epi_model_name}"),
    shell:
        """
        pixi run python src/run_epi_model.py \
            --dataset {wildcards.dataset} \
            --years {wildcards.year} \
            --realizations {wildcards.realization} \
            --epi-model-name {wildcards.epi_model_name}
        """
