import re
from src.inputs import DATASETS, EPI_MODEL_NAME, ALT_EPI_MODEL_NAME, get_batches

EPI_MODELS = [EPI_MODEL_NAME, ALT_EPI_MODEL_NAME]


wildcard_constraints:
    epi_model_name="|".join(re.escape(m) for m in EPI_MODELS),


def get_download_file(dataset, realization, year):
    return f"results/downloads/{dataset}/{realization}_{year}.txt"


def get_mean_temperature_file(dataset, realization, year):
    return f"results/mean_temperatures/{dataset}/{realization}_{year}.nc"


def get_epi_result_file(dataset, realization, year, epi_model_name):
    return f"results/{epi_model_name}/{dataset}/{realization}_{year}.nc"


def get_temperature_figure_data_file(native_or_downscaled):
    return f"results/figure_data/{native_or_downscaled}/temperature_time_series.nc"


def get_figure_data_files(epi_model_name, native_or_downscaled):
    return [
        f"results/figure_data/{native_or_downscaled}/{epi_model_name}/{analysis}.nc"
        for analysis in [
            "current",
            "mean",
            "change_example",
            "location",
            "later_mean",
            "even_later_mean",
            "change_example_others",
            "location_others",
            "change_summary",
        ]
    ]


def get_figure_files(native_or_downscaled):
    return [
        f"figures/{native_or_downscaled}/{fig_name}.svg"
        for fig_name in [
            "figure_1",
            "figure_2",
            "figure_3",
            "figure_4",
            "figure_S1",
            "figure_S2",
            "figure_S3",
            "figure_S4",
            "figure_S5",
            "figure_S6",
            "figure_S7",
            "figure_S8",
        ]
    ]


download_files = [
    get_download_file(dataset, realization, year)
    for dataset, meta in DATASETS.items()
    for realization in meta["subset"]["realizations"]
    for year in meta["subset"]["years"]
]

mean_temperature_files = [
    get_mean_temperature_file(dataset, realization, year)
    for dataset, meta in DATASETS.items()
    for realization in meta["subset"]["realizations"]
    for year in meta["subset"]["years"]
]

epi_result_files = [
    get_epi_result_file(dataset, realization, year, epi_model_name)
    for dataset, meta in DATASETS.items()
    for realization in meta["subset"]["realizations"]
    for year in meta["subset"]["years"]
    for epi_model_name in EPI_MODELS
]

figure_data_files = [
    file
    for native_or_downscaled in ["native", "downscaled"]
    for epi_model_name in EPI_MODELS
    for file in get_figure_data_files(epi_model_name, native_or_downscaled)
] + [
    get_temperature_figure_data_file(native_or_downscaled)
    for native_or_downscaled in ["native", "downscaled"]
]

figure_files = get_figure_files(native_or_downscaled="downscaled") + get_figure_files(
    native_or_downscaled="native"
)

figure_files_png = [f.replace(".svg", ".png") for f in figure_files]


rule all:
    input:
        figure_files,


rule figures_png:
    input:
        figure_files,
    output:
        figure_files_png,
    shell:
        r"""
        for svg in {input}; do
            png="${{svg%.svg}}.png"
            echo "Converting $svg -> $png"
            inkscape "$svg" --export-type=png --export-filename="$png"
        done
        """


rule downloads:
    input:
        download_files,


rule results:
    input:
        mean_temperature_files,
        epi_result_files,


for dataset_name in DATASETS:
    for batch_index, batch in enumerate(get_batches(dataset_name)):

        rule:
            name:
                f"download_data_{dataset_name}_{batch_index}"
            input:
                "src/inputs.py",
                "src/download_data.py",
            output:
                [
                    get_download_file(dataset_name, realization, year)
                    for realization in batch["realizations"]
                    for year in batch["years"]
                ],
            log:
                f"logs/download_data/{dataset_name}_batch{batch_index}.log",
            params:
                dataset=dataset_name,
                years=batch["years"],
                realizations=batch["realizations"],
            shell:
                """
                pixi run python src/download_data.py \
                    --dataset {params.dataset} \
                    --years {params.years} \
                    --realizations {params.realizations} \
                    >{log} 2>&1
                """

        rule:
            name:
                f"calc_mean_temperatures_{dataset_name}_{batch_index}"
            input:
                [
                    get_download_file(dataset_name, realization, year)
                    for realization in batch["realizations"]
                    for year in batch["years"]
                ],
                "src/inputs.py",
                "src/calc_mean_temperatures.py",
            output:
                [
                    get_mean_temperature_file(dataset_name, realization, year)
                    for realization in batch["realizations"]
                    for year in batch["years"]
                ],
            log:
                f"logs/calc_mean_temperatures/{dataset_name}_batch{batch_index}.log",
            params:
                dataset=dataset_name,
                years=batch["years"],
                realizations=batch["realizations"],
            shell:
                """
                pixi run python src/calc_mean_temperatures.py \
                    --dataset {params.dataset} \
                    --years {params.years} \
                    --realizations {params.realizations} \
                    >{log} 2>&1
                """

        for epi_model_name in EPI_MODELS:

            rule:
                name:
                    f"run_epi_model_{epi_model_name}_{dataset_name}_{batch_index}"
                input:
                    [
                        get_download_file(dataset_name, realization, year)
                        for realization in batch["realizations"]
                        for year in batch["years"]
                    ],
                    "src/inputs.py",
                    "src/run_epi_model.py",
                output:
                    [
                        get_epi_result_file(
                            dataset_name, realization, year, epi_model_name
                        )
                        for realization in batch["realizations"]
                        for year in batch["years"]
                    ],
                log:
                    f"logs/run_epi_model/"
                    f"{epi_model_name}_{dataset_name}_batch{batch_index}.log",
                resources:
                    mem_mb_per_cpu=16000,
                params:
                    dataset=dataset_name,
                    years=batch["years"],
                    realizations=batch["realizations"],
                    epi_model_name=epi_model_name,
                shell:
                    """
                    pixi run python src/run_epi_model.py \
                        --dataset {params.dataset} \
                        --years {params.years} \
                        --realizations {params.realizations} \
                        --epi-model-name {params.epi_model_name} \
                        >{log} 2>&1
                    """


rule make_temperature_figure_data:
    input:
        lambda wildcards: [
            file
            for file in mean_temperature_files
            if (
                ("downscaled" in file)
                == (wildcards.native_or_downscaled == "downscaled")
            )
        ],
        "src/make_figure_data.py",
        "src/figure_data_functions.py",
    output:
        get_temperature_figure_data_file("{native_or_downscaled}"),
    params:
        opts=lambda wildcards: (
            "--temperature --downscaled"
            if wildcards.native_or_downscaled == "downscaled"
            else "--temperature"
        ),
    shell:
        "pixi run python src/make_figure_data.py {params.opts}"


rule make_figure_data:
    input:
        lambda wildcards: [
            file
            for file in epi_result_files
            if wildcards.epi_model_name in file
            and (
                ("downscaled" in file)
                == (wildcards.native_or_downscaled == "downscaled")
            )
        ],
        "src/make_figure_data.py",
        "src/figure_data_functions.py",
    output:
        get_figure_data_files("{epi_model_name}", "{native_or_downscaled}"),
    params:
        opts=lambda wildcards: (
            f"--downscaled --epi-model-name {wildcards.epi_model_name}"
            if wildcards.native_or_downscaled == "downscaled"
            else f"--epi-model-name {wildcards.epi_model_name}"
        ),
    shell:
        "pixi run python src/make_figure_data.py {params.opts}"


rule make_figures:
    input:
        lambda wildcards: [
            file
            for file in figure_data_files
            if (wildcards.native_or_downscaled in file)
        ],
        "src/inputs.py",
        "src/make_figures.py",
        "src/plotting_functions.py",
    output:
        get_figure_files("{native_or_downscaled}"),
    params:
        opts=lambda wildcards: (
            "--downscaled" if wildcards.native_or_downscaled == "downscaled" else ""
        ),
    shell:
        "pixi run python src/make_figures.py {params.opts}"
