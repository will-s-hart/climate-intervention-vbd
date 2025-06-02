arise_control_realizations = list(range(10))
arise_control_year_ranges = ["2020-2029", "2060-2069"]
arise_feedback_realizations = list(range(10))
arise_feedback_year_ranges = ["2060-2069"]

glens_control_realizations = list(range(3))
glens_control_year_ranges = ["2020-2029", "2060-2069", "2080-2089"]
glens_feedback_realizations = list(range(20))
glens_feedback_year_ranges = ["2020-2029", "2060-2069", "2080-2089"]


rule arise_control:
    input:
        expand(
            "results/downloads/arise_control_{realization}_{year_range}.txt",
            realization=arise_control_realizations,
            year_range=arise_control_year_ranges,
        ),
    output:
        "results/arise_control.nc",
    shell:
        """
        python scripts/run_epi_model.py --dataset arise_control
        """


rule arise_feedback:
    input:
        expand(
            "results/downloads/arise_feedback_{realization}_{year_range}.txt",
            realization=arise_feedback_realizations,
            year_range=arise_feedback_year_ranges,
        ),
    output:
        "results/arise_feedback.nc",
    shell:
        """
        python scripts/run_epi_model.py --dataset arise_feedback
        """


rule glens_control:
    input:
        expand(
            "results/downloads/glens_control_{realization}_{year_range}.txt",
            realization=glens_control_realizations,
            year_range=glens_control_year_ranges,
        ),
    output:
        "results/glens_control.nc",
    shell:
        """
        python scripts/run_epi_model.py --dataset glens_control
        """


rule glens_feedback:
    input:
        expand(
            "results/downloads/glens_feedback_{realization}_{year_range}.txt",
            realization=glens_feedback_realizations,
            year_range=glens_feedback_year_ranges,
        ),
    output:
        "results/glens_feedback.nc",
    shell:
        """
        python scripts/run_epi_model.py --dataset glens_feedback
        """


rule arise_control_data:
    input:
        expand(
            "results/downloads/arise_control_{realization}_{year_range}.txt",
            realization=arise_control_realizations,
            year_range=arise_control_year_ranges,
        ),


rule arise_feedback_data:
    input:
        expand(
            "results/downloads/arise_feedback_{realization}_{year_range}.txt",
            realization=arise_feedback_realizations,
            year_range=arise_feedback_year_ranges,
        ),


rule glens_control_data:
    input:
        expand(
            "results/downloads/glens_control_{realization}_{year_range}.txt",
            realization=glens_control_realizations,
            year_range=glens_control_year_ranges,
        ),


rule glens_feedback_data:
    input:
        expand(
            "results/downloads/glens_feedback_{realization}_{year_range}.txt",
            realization=glens_feedback_realizations,
            year_range=glens_feedback_year_ranges,
        ),


rule download_data:
    output:
        "results/downloads/{dataset}_{realization}_{year_range}.txt",
    shell:
        """
        python scripts/download_data.py --dataset {wildcards.dataset} --year-range {wildcards.year_range} --realizations {wildcards.realization}
        """
