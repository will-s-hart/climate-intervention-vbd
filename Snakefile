DATASETS = {
    "arise_control": {
        "realizations": list(range(10)),
        "year_ranges": ["2020-2029", "2060-2069"],
    },
    "arise_feedback": {
        "realizations": list(range(10)),
        "year_ranges": ["2060-2069"],
    },
    "glens_control": {
        "realizations": list(range(3)),
        "year_ranges": ["2020-2029", "2060-2069", "2080-2089"],
    },
    "glens_feedback": {
        "realizations": list(range(3)),
        "year_ranges": ["2020-2029", "2060-2069", "2080-2089"],
    },
    "glens_feedbackrest": {
        "realizations": list(range(3, 20)),
        "year_ranges": ["2020-2029", "2060-2069", "2080-2089"],
    },
}


def get_download_file(dataset, realization, year_range):
    return f"results/downloads/{dataset}_{realization}_{year_range}.txt"


def get_result_file(dataset, realization):
    return f"results/{dataset}_{realization}.nc"


download_files = [
    get_download_file(dataset, r, y)
    for dataset, meta in DATASETS.items()
    for r in meta["realizations"]
    for y in meta["year_ranges"]
]

result_files = [
    get_result_file(dataset, r)
    for dataset, meta in DATASETS.items()
    for r in meta["realizations"]
]


# Final targets
rule all:
    input:
        download_files + result_files,


rule download_data:
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
    output:
        get_result_file("{dataset}", "{realization}"),
    shell:
        """
        pixi run python scripts/run_epi_model.py \
            --dataset {wildcards.dataset} \
            --realizations {wildcards.realization}
        """
