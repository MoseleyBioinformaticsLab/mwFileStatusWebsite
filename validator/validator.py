#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
~~~~~~~

This script contains methods for validating all available mwTab data files, creating log files, and generating a JSON
file containing the validation metadata.
"""
import mwtab
import json
from datetime import datetime


MW_REST_URL = "https://www.metabolomicsworkbench.org/rest/study/analysis_id/{}/mwtab/{}"
VALIDATION_LOG_HEADER = """Validation Log
{}
mwtab version: {}
Study ID:      {}
Analysis ID:   {}
File format:   {}
"""


def validate_mwtab_files(verbose=False):
    """

    :return:
    """
    if verbose:
        print("Running mwTab file validation.")
        print("\tmwtab version:", mwtab.__version__)

    try:
        study_analysis_dict = mwtab.mwrest.pull_study_analysis()

        # count the number of present studies and analyses
        num_studies = len(study_analysis_dict)
        num_analyses = sum([len(study_analysis_dict[k]) for k in study_analysis_dict])
        if verbose:
            print("{} studies found".format(num_studies))
            print("{} analyses found".format(num_analyses))

    # cannot access Metabolomics Workbench REST server
    except Exception as e:
        print("Unable to access https://www.metabolomicsworkbench.org/")
        print(e)
        exit()

    # setup some variables for collecting validation statuses
    validation_dict = {study_id: {
        analysis_id: [] for analysis_id in sorted(study_analysis_dict[study_id])
    } for study_id in sorted(study_analysis_dict.keys())}

    for study_id in sorted(study_analysis_dict.keys()):

        if verbose:
            print("Validating study:", study_id)

        for analysis_id in study_analysis_dict[study_id]:

            if verbose:
                print("\t", analysis_id)

            for file_format in ("txt", "json"):

                validation_log = VALIDATION_LOG_HEADER.format(str(datetime.now()), mwtab.__version__, study_id, analysis_id, file_format)

                try:
                    mwtabfile = next(mwtab.read_files(MW_REST_URL.format(analysis_id, file_format)))
                    _, error_log_str = mwtab.validate_file(mwtabfile, metabolites=False)

                    # file passed validation (no errors saved to error log)
                    if not error_log_str:
                        validation_dict[study_id].setdefault(analysis_id, list()).append([file_format, "Passing"])
                        error_log_str = "Passing"

                    # file contains validation errors
                    else:
                        validation_dict[study_id].setdefault(analysis_id, list()).append([file_format, "Validation Error"])

                    validation_log += error_log_str

                # error in accessing Metabolomics Workbench REST API for specific file
                except (TypeError, IndexError) as e:
                    validation_dict[study_id].setdefault(analysis_id, list()).append([file_format, "Parsing Error"])
                    validation_log += "Parsing Error\n" + str(e)

                except Exception as e:
                    validation_dict[study_id].setdefault(analysis_id, list()).append([file_format, "Missing/Blank"])
                    validation_log += "Missing/Blank\n" + str(e)

                with open("../docs/validation_logs/{}_{}.log".format(analysis_id, file_format), "w") as fh:
                    fh.write(validation_log)



        #
        #         except Exception as e:
        #
        #             if type(e) in (TypeError, IndexError):
        #                 validation_dict[study_id].setdefault(analysis_id, list()).append([
        #                     file_format,
        #                     "Parsing Error",
        #                     "red",
        #                     MW_REST_URL.format(analysis_id, file_format),
        #                     REPO_PATH.format(analysis_id, file_format)
        #                 ])
        #             else:
        #                 validation_dict[study_id].setdefault(analysis_id, list()).append([
        #                     file_format,
        #                     "Missing/Blank",
        #                     "lightgrey",
        #                     MW_REST_URL.format(analysis_id, file_format),
        #                     REPO_PATH.format(analysis_id, file_format)
        #                 ])
        #
        #             with open("docs/validation_logs/{}_{}.log".format(analysis_id, file_format), "w") as fh:
        #                 fh.write(str(e))

    # export validation status dictionary
    with open("tmp.json", "w") as fh:
        fh.write(json.dumps(validation_dict))

    return validation_dict


if __name__ == "__main__":
    validate_mwtab_files(True)
