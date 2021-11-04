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
import re
from datetime import datetime


MW_REST_URL = "https://www.metabolomicsworkbench.org/rest/study/analysis_id/{}/mwtab/{}"


def validate_mwtab_files(output_file="tmp.json", verbose=False):
    """

    :return:
    """
    if verbose:
        print("Running mwTab file validation.")
        print("\tmwtab version:", mwtab.__version__)

    try:
        study_analysis_dict = mwtab.mwrest._pull_study_analysis()

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
    validation_dict = {
        study_id: {
            "params": {},
            "analyses": {
                analysis_id: {
                    "params": {
                        "ANALYSIS_ID": analysis_id
                    },
                    "status": {
                        "txt": None,
                        "json": None
                    }
                } for analysis_id in sorted(study_analysis_dict[study_id])
            }
        } for study_id in sorted(study_analysis_dict.keys())
    }

    for study_id in sorted(study_analysis_dict.keys()):

        if verbose:
            print("Validating study:", study_id)

        for analysis_id in study_analysis_dict[study_id]:

            if verbose:
                print("\t", analysis_id)

            for file_format in ("txt", "json"):

                try:
                    mwtabfile = next(mwtab.read_files(MW_REST_URL.format(analysis_id, file_format)))
                    validated_mwtabfile, validation_log = mwtab.validate_file(mwtabfile, metabolites=False)
                    status_str = re.search(r'Status.*', validation_log).group(0).split(': ')[1]
                    if status_str == 'Passing':
                        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Passing"
                    elif status_str == 'Contains Validation Errors':
                        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Validation Error"
                    validation_dict[study_id]["params"] = mwtabfile["STUDY"]

                # error in accessing Metabolomics Workbench REST API for specific file
                except (TypeError, IndexError) as e:
                    validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Parsing Error"
                    validation_log = mwtab.validator.VALIDATION_LOG_HEADER.format(
                        str(datetime.now()),
                        mwtab.__version__,
                        MW_REST_URL.format(analysis_id, file_format),
                        study_id,
                        analysis_id,
                        file_format
                    )
                    validation_log += "Status: Parsing Error\n" + str(e)

                except Exception as e:
                    validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Missing/Blank"
                    validation_log = mwtab.validator.VALIDATION_LOG_HEADER.format(
                        str(datetime.now()),
                        mwtab.__version__,
                        MW_REST_URL.format(analysis_id, file_format),
                        study_id,
                        analysis_id,
                        file_format
                    )
                    validation_log += "Status: Missing/Blank\n" + str(e)

                with open("../docs/validation_logs/{}_{}.log".format(analysis_id, file_format), "w") as fh:
                    fh.write(validation_log)

    # export validation status dictionary
    with open(output_file, "w") as fh:
        fh.write(json.dumps(validation_dict))

    return validation_dict


if __name__ == "__main__":
    validate_mwtab_files("tmp.json", True)
