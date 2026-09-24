import pathlib

from snakemake.exceptions import WorkflowError

from src.inputs import (
    DATASETS,
    EPI_MODEL_NAME,
    ALT_EPI_MODEL_NAME,
    get_batches,
    get_downscaled_raw_data_path,
)

# Gitignored machine-specific settings; currently only downscaled_raw_dir, the root of
# the (not publicly available) raw downscaled data. --config overrides it.
LOCAL_CONFIG_PATH = pathlib.Path("config.local.yaml")
if LOCAL_CONFIG_PATH.exists():

    configfile: LOCAL_CONFIG_PATH


EPI_MODELS = [EPI_MODEL_NAME, ALT_EPI_MODEL_NAME]

# Figure data products generated for both epi models, and those generated only for the
# primary (EPI_MODEL_NAME) model
COMMON_FIGURE_DATA_NAMES = [
    "mean",
    "change_example",
    "location",
]
PRIMARY_FIGURE_DATA_NAMES = [
    "current",
    "later_mean",
    "even_later_mean",
    "change_example_others",
]


wildcard_constraints:
    native_or_downscaled="native|downscaled",


def get_downscaled_raw_dir():
    downscaled_raw_dir = config.get("downscaled_raw_dir")
    if downscaled_raw_dir is None:
        raise WorkflowError(
            "The downscaled datasets are formatted from raw downscaled data, whose "
            "location is not set. Create config.local.yaml containing\n"
            "    downscaled_raw_dir: /path/to/raw/downscaled/data\n"
            "or pass --config downscaled_raw_dir=/path/to/raw/downscaled/data. "
            "Without that data, build the native-resolution figures only with the "
            "`native` target."
        )
    # Relative paths are left as given; Snakemake resolves them against the working
    # directory, which is also where the jobs run
    return pathlib.Path(downscaled_raw_dir).expanduser()


def get_download_file(dataset, realization, year):
    return f"results/downloads/{dataset}/{realization}_{year}.txt"


def get_mean_temperature_file(dataset, realization, year):
    return f"results/mean_temperatures/{dataset}/{realization}_{year}.nc"


def get_epi_result_file(dataset, realization, year, epi_model_name):
    return f"results/{epi_model_name}/{dataset}/{realization}_{year}.nc"


def get_temperature_figure_data_file(native_or_downscaled):
    return f"results/figure_data/{native_or_downscaled}/temperature_time_series.nc"


def get_figure_data_files(epi_model_name, native_or_downscaled):
    analyses = COMMON_FIGURE_DATA_NAMES + (
        PRIMARY_FIGURE_DATA_NAMES if epi_model_name == EPI_MODEL_NAME else []
    )
    return [
        f"results/figure_data/{native_or_downscaled}/{epi_model_name}/{analysis}.nc"
        for analysis in analyses
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


# Needs no downscaled data, so builds without downscaled_raw_dir set
rule native:
    input:
        get_figure_files("native"),


rule downscaled:
    input:
        get_figure_files("downscaled"),


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
                f"download_and_format_data_{dataset_name}_{batch_index}"
            input:
                "src/inputs.py",
                "src/download_and_format_data.py",
                # Downscaled datasets are formatted from raw files; dataset_name and
                # batch bound as default arguments so each generated rule keeps its
                # own rather than closing over the loop variables
                downscaled_raw_data=(
                    lambda wildcards, dataset_name=dataset_name, batch=batch: (
                        [
                            get_downscaled_raw_data_path(
                                dataset_name,
                                realization,
                                year,
                                get_downscaled_raw_dir(),
                            )
                            for realization in batch["realizations"]
                            for year in batch["years"]
                        ]
                        if "downscaled" in dataset_name
                        else []
                    )
                ),
            output:
                [
                    get_download_file(dataset_name, realization, year)
                    for realization in batch["realizations"]
                    for year in batch["years"]
                ],
            log:
                f"logs/download_and_format_data/{dataset_name}_batch{batch_index}.log",
            params:
                dataset=dataset_name,
                years=batch["years"],
                realizations=batch["realizations"],
                opts=lambda wildcards, dataset_name=dataset_name: (
                    f"--downscaled-raw-dir {get_downscaled_raw_dir()}"
                    if "downscaled" in dataset_name
                    else ""
                ),
            shell:
                """
                pixi run python src/download_and_format_data.py \
                    --dataset {params.dataset} \
                    --years {params.years} \
                    --realizations {params.realizations} \
                    {params.opts} \
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
        "src/inputs.py",
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


for epi_model_name in EPI_MODELS:

    rule:
        name:
            f"make_figure_data_{epi_model_name}"
        input:
            # epi_model_name bound as a default argument so each generated rule keeps
            # its own model rather than closing over the loop variable
            lambda wildcards, epi_model_name=epi_model_name: [
                file
                for file in epi_result_files
                if epi_model_name in file
                and (
                    ("downscaled" in file)
                    == (wildcards.native_or_downscaled == "downscaled")
                )
            ],
            "src/inputs.py",
            "src/make_figure_data.py",
            "src/figure_data_functions.py",
        output:
            get_figure_data_files(epi_model_name, "{native_or_downscaled}"),
        params:
            epi_model_name=epi_model_name,
            downscaled_flag=lambda wildcards: (
                "--downscaled"
                if wildcards.native_or_downscaled == "downscaled"
                else ""
            ),
        shell:
            """
            pixi run python src/make_figure_data.py {params.downscaled_flag} \
                --epi-model-name {params.epi_model_name}
            """


rule make_figures:
    input:
        lambda wildcards: [
            file
            for file in figure_data_files
            if (wildcards.native_or_downscaled in file)
        ],
        "data/arbo_occ_thinned.csv",
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
