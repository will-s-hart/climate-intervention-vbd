DATASETS = {
    "arise_control": {
        "realizations": list(range(10)),
        "year_ranges": [
            "2024-2034",
            "2035-2044",
            "2045-2054",
            "2055-2064",
        ],
    },
    "arise_feedback": {
        "realizations": list(range(10)),
        "year_ranges": [
            "2035-2044",
            "2045-2054",
            "2055-2064",
        ],
    },
}
EPI_MODELS = ["mordecai_ae_aegypti_niche", "kaye_ae_aegypti_niche"]


def get_download_file(dataset, realization, year_range):
    return f"results/downloads/{dataset}_{realization}_{year_range}.txt"


def get_result_file(dataset, realization, epi_model_name):
    return f"results/{epi_model_name}/{dataset}_{realization}.nc"


download_files = [
    get_download_file(dataset, realization, year_range)
    for dataset, meta in DATASETS.items()
    for realization in meta["realizations"]
    for year_range in meta["year_ranges"]
]

result_files = [
    get_result_file(dataset, realization, epi_model_name)
    for dataset, meta in DATASETS.items()
    for realization in meta["realizations"]
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
        "scripts/inputs.py",
        "scripts/download_data.py",
    output:
        get_download_file("{dataset}", "{realization}", "{year_range}"),
    shell:
        """
        pixi run python scripts/download_data.py \
            --dataset {wildcards.dataset} \
            --year-range {wildcards.year_range} \
            --realizations {wildcards.realization}
        """


rule run_epi_model:
    input:
        lambda wildcards: [
            get_download_file(wildcards.dataset, wildcards.realization, y)
            for y in DATASETS[wildcards.dataset]["year_ranges"]
        ],
        "scripts/inputs.py",
        "scripts/run_epi_model.py",
    output:
        get_result_file("{dataset}", "{realization}", "{epi_model_name}"),
    shell:
        """
        pixi run python scripts/run_epi_model.py \
            --dataset {wildcards.dataset} \
            --realizations {wildcards.realization} \
            --epi-model-name {wildcards.epi_model_name}
        """
