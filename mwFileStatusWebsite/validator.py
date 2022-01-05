#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validator.py
~~~~~~~~~~~~

This script contains methods for validating all available mwTab data files, creating log files, and generating a JSON
file containing the validation metadata.
"""
import mwtab
import json
import re
from datetime import datetime
from os.path import join
from time import sleep


MW_REST_URL = "https://www.metabolomicsworkbench.org/rest/study/analysis_id/{}/mwtab/{}"


def retrieve_mwtab_files(verbose=False):
    """Method for retrieving a dictionary of Metabolomics Workbench file identifiers.

    Example:
    {
        'ST000001': [
            'AN000001',
            ...
        ],
        ...
    }

    :param bool verbose: Run in verbose mode.
    :return: Dictionary of study IDs (keys) and their associated lists of analysis IDs (values).
    """
    try:
        study_analysis_dict = mwtab.mwrest._pull_study_analysis()

        # count the number of present studies and analyses
        num_studies = len(study_analysis_dict)
        num_analyses = sum([len(study_analysis_dict[k]) for k in study_analysis_dict])
        if verbose:
            print("{} studies found".format(num_studies))
            print("{} analyses found".format(num_analyses))

        return study_analysis_dict

    # cannot access Metabolomics Workbench REST server
    except Exception as e:
        print("Unable to access https://www.metabolomicsworkbench.org/")
        print(e)
        exit()


def create_validation_dict(study_analysis_dict):
    """

    :param study_analysis_dict:
    :return:
    """
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
    return validation_dict


def validate(validation_dict, study_id, analysis_id, file_format):
    """

    :param validation_dict:
    :param study_id:
    :param analysis_id:
    :param file_format:
    :return:
    """
    mwtabfile = next(mwtab.read_files(MW_REST_URL.format(analysis_id, file_format)))
    sleep(1)
    validated_mwtabfile, validation_log = mwtab.validate_file(mwtabfile, metabolites=False)
    status_str = re.search(r'Status.*', validation_log).group(0).split(': ')[1]

    if status_str == 'Passing':
        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Passing"
    elif status_str == 'Contains Validation Errors':
        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Validation Error"

    if not validation_dict[study_id]["params"]:
        validation_dict[study_id]["params"] = mwtabfile["STUDY"]

    return validation_log


def validate_mwtab_files(
        input_file=None, input_dict=None,
        logs_path='docs/validation_logs', output_file="tmp.json", verbose=False
):

    if verbose:
        print("Running mwTab file validation.")
        print("\tmwtab version:", mwtab.__version__)

    # collect dictionary of studies and their analyses
    if input_file:
        study_analysis_dict = dict()
    elif input_dict:
        study_analysis_dict = input_dict
    else:
        study_analysis_dict = retrieve_mwtab_files(verbose)

    # create the validation dict
    validation_dict = create_validation_dict(study_analysis_dict)

    for study_id in sorted(study_analysis_dict.keys()):

        if verbose:
            print("Validating study:", study_id)

        for analysis_id in study_analysis_dict[study_id]:

            if verbose:
                print("\t", analysis_id)

            for file_format in ("txt", "json"):

                try:
                    validation_log = validate(validation_dict, study_id, analysis_id, file_format)

                except Exception as e:
                    # error is one of; 1) temporary server error, 2) source is blank, or 3) source cannot be parsed

                    # check to see if temporary server error
                    fixed = False
                    for x in range(3):  # try three times to see if there is a temporary server error
                        try:
                            validation_log = validate(validation_dict, study_id, analysis_id, file_format)
                            fixed = True
                            break
                        except Exception:
                            pass

                    # not temporary server error, either source is blank or source cannot be parsed
                    if not fixed:
                        status = ""
                        # blank source given
                        if type(e) == ValueError and e.args[0] == "Blank input string retrieved from source.":
                            validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Missing/Blank"
                        else:
                            validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Parsing Error"

                        validation_log = mwtab.validator.VALIDATION_LOG_HEADER.format(
                            str(datetime.now()),
                            mwtab.__version__,
                            MW_REST_URL.format(analysis_id, file_format),
                            study_id,
                            analysis_id,
                            file_format
                        )
                        validation_log += "\nStatus:" + status + "\n" + str(e)

                with open(join(logs_path, '{}_{}.log'.format(analysis_id, file_format)), "w") as fh:
                    fh.write(validation_log)

    # export validation status dictionary
    with open(output_file, "w") as fh:
        fh.write(json.dumps(validation_dict))

    return validation_dict


if __name__ == "__main__":
    validate_mwtab_files(output_file="tmp.json", verbose=True)
