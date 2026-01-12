from src.inputs import DATASETS, EPI_MODEL_NAME, ALT_EPI_MODEL_NAME

EPI_MODELS = [EPI_MODEL_NAME, ALT_EPI_MODEL_NAME]


def get_download_file(dataset, realization, year):
    return f"results/downloads/{dataset}/{realization}_{year}.txt"


def get_result_file(dataset, realization, year, epi_model_name):
    return f"results/{epi_model_name}/{dataset}/{realization}_{year}.nc"


def get_figure_data_files(epi_model_name, native_or_downscaled):
    return [
        f"results/figure_data/{native_or_downscaled}/{epi_model_name}/{analysis}.nc"
        for analysis in [
            "mean",
            "change_example",
            "location",
            "later_mean",
            "even_later_mean",
            "change_example_others",
            "location",
            "trend_example",
            "change_summary",
            "trend_summary",
        ]
    ]


def get_figure_files(native_or_downscaled):
    return [
        f"figures/{native_or_downscaled}/{fig_name}.svg"
        for fig_name in [
            "figure_1",
            "figure_2",
            "figure_S1",
            "figure_S2",
            "figure_S3",
            "figure_S4",
            "figure_S5",
            "figure_S6",
            "figure_S7",
        ]
    ]


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

figure_data_files = [
    file
    for native_or_downscaled in ["native", "downscaled"]
    for epi_model_name in EPI_MODELS
    for file in get_figure_data_files(epi_model_name, native_or_downscaled)
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


rule make_figure_data:
    input:
        result_files,
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
        figure_data_files,
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
