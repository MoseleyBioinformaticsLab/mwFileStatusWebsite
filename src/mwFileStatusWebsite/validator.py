#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validator.py
~~~~~~~~~~~~

This script contains methods for validating all available mwTab data files, creating log files, and generating a JSON
file containing the validation metadata.
"""
import mwFileStatusWebsite.compare
import mwtab
import json
import re
from datetime import datetime
from os.path import join
from time import sleep


MW_REST_URL = "https://www.metabolomicsworkbench.org/rest/study/analysis_id/{}/mwtab/{}"
SLEEP_TIME = 1
NUM_TRIES = 3


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
    """Method for creating a null structured validation dictionary.

    :param study_analysis_dict: Dictionary of Metabolomics study IDs (key) and lists of their associated analysis IDs
    (value).
    :type study_analysis_dict: dict

    :return: Returns a structured dictionary to contain analysis validation statuses and associated study data.
    :rtype: dict
    """
    # setup some variables for collecting validation statuses
    validation_dict = {
        study_id: {
            "params": {},  # TODO:Change to STUDY_params
            "analyses": {
                analysis_id: {
                    "params": {
                        "ANALYSIS_ID": analysis_id
                    },
                    "status": {
                        "txt": None,
                        "json": None
                    },
                    'issues': {
                        'txt': {
                            'value': False,
                            'consistency': False,
                            'format': False,
                            },
                        'json': {
                            'value': False,
                            'consistency': False,
                            'format': False,
                            }
                        }
                } for analysis_id in sorted(study_analysis_dict[study_id])
            }
        } for study_id in sorted(study_analysis_dict.keys())
    }
    return validation_dict


def _validate(validation_dict, study_id, analysis_id, file_format, save_path=None):
    """Helper function for performing validation of a specified mwTab data file given the files; study ID, analysis ID,
    and file format (.txt or .json).

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param study_id: Metabolomics Workbench study ID string (eg. ST000001).
    :type study_id: str
    :param analysis_id: Metabolomics Workbench analysis ID string (eg. AN000001).
    :type analysis_id: str
    :param file_format: File format extension string (either: 'txt' or 'json').
    :type file_format: str
    :param save_path: Directory path for retrieved Metabolomics Workbench analysis data files to be saved in.
    :type save_path: str

    :return: Tuple containing of the validated mwtab file object and the string validation log.
    :rtype: tuple
    """
    mwtabfile = next(mwtab.read_files(MW_REST_URL.format(analysis_id, file_format)))

    # allows saving out the retrieved non-validated mwTab analysis files.
    if save_path:
        with open(join(save_path, analysis_id + '.' + file_format), 'w', encoding='utf-8') as fh:
            mwtabfile.write(fh, 'mwtab' if file_format == 'txt' else 'json')

    sleep(SLEEP_TIME)

    validation_log, validation_json = mwtab.validate_file(mwtabfile)

    # parse validation status (e.g. "Passing") from validation log
    status_str = re.search(r'Status.*', validation_log).group(0).split(': ')[1]
    if status_str == 'Passing':
        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Passing"
    elif re.search(r'Number of Issues: (\d+)', validation_log).group(1) == re.search(r'Number of Warnings: (\d+)', validation_log).group(1):
        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Warnings Only"
    elif status_str == 'Contains Validation Issues':
        validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Validation Error"
    
    for issue in validation_json:
        if issue['message'].startswith('Error'):
            if 'value' in issue['tags']:
                validation_dict[study_id]["analyses"][analysis_id]["issues"][file_format]['value'] = True
            if 'consistency' in issue['tags']:
                validation_dict[study_id]["analyses"][analysis_id]["issues"][file_format]['consistency'] = True
            if 'format' in issue['tags']:
                validation_dict[study_id]["analyses"][analysis_id]["issues"][file_format]['format'] = True

    # parse out STUDY block parameters
    if not validation_dict[study_id]["params"]:
        validation_dict[study_id]["params"] = mwtabfile["STUDY"]

    return mwtabfile, validation_log


def validate(validation_dict, study_id, analysis_id, file_format, save_path=None):
    """Method for validating a given Metabolomics Workbench mwTab file.

    Creates a validation log and adds validation status to the given validation_dict dictionary. Fetches files using the
    ``mwtab`` Python3 packages built in methods for accessing Metabolomics Workbench's REST API. Performs three attempts
    to retrieve a file before labeling it as "Missing/Blank".

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param study_id: Metabolomics Workbench study ID string (eg. ST000001).
    :type study_id: str
    :param analysis_id: Metabolomics Workbench analysis ID string (eg. AN000001).
    :type analysis_id: str
    :param file_format: File format extension string (either: 'txt' or 'json').
    :type file_format: str
    :param save_path: Directory path for retrieved Metabolomics Workbench analysis data files to be saved in.
    :type save_path: str

    :return: Tuple containing of the validated mwtab file object and the string validation log.
    :rtype: tuple
    """
    error = False

    try:
        validated_mwtabfile, validation_log = _validate(validation_dict, study_id, analysis_id, file_format, save_path)

    except Exception as e:
        # error is one of; 1) temporary server error, 2) source is blank, or 3) source cannot be parsed

        # check to see if temporary server error
        error = True
        for x in range(NUM_TRIES):  # try three times to see if there is a temporary server error
            try:
                validated_mwtabfile, validation_log = _validate(validation_dict, study_id, analysis_id, file_format)
                error = False
                break
            except Exception:
                pass

        # not temporary server error, either source is blank or source cannot be parsed
        if error:
            # blank source given
            if type(e) == ValueError and e.args[0] == "Blank input string retrieved from source.":
                validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Missing/Blank"
            else:
                validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] = "Parsing Error"

            # create validation log for missing or unparsable files.
            validation_log = mwtab.validator.VALIDATION_LOG_HEADER.format(
                str(datetime.now()),
                mwtab.__version__,
                MW_REST_URL.format(analysis_id, file_format),
                study_id,
                analysis_id,
                file_format
            )
            validation_log += \
                "\nStatus:" + \
                validation_dict[study_id]["analyses"][analysis_id]["status"][file_format] + \
                "\n" + str(e)

    if not error:
        return validated_mwtabfile, validation_log
    else:
        return {}, validation_log


def validate_mwtab_rest(input_dict=None, logs_path='validation_logs', output_file="tmp.json",
                        verbose=False, save_path=None):
    """Method for validating all available Metabolomics Workbench mwTab formatted data files.

    :param input_dict: Dictionary of Metabolomics study IDs (key) and lists of their associated analysis IDs (value).
    :type input_dict: dict
    :param logs_path: File path to the directory validation logs are to be saved to.
    :type logs_path: str
    :param output_file: File path for the structured dictionary containing analyses statuses and other study information
    to be saved to.
    :type output_file: str
    :param verbose: Run in verbose mode.
    :type verbose: bool
    :param save_path: Directory path for retrieved Metabolomics Workbench analysis data files to be saved in.
    :type save_path: str
    :return: Structured dictionary containing analyses statuses and other study information.
    :rtype: dict
    """
    if verbose:
        print("Running mwTab file validation.")
        print("\tmwtab version:", mwtab.__version__)

    # collect dictionary of studies and their analyses
    if input_dict:
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

            # retrieve file in both its 'txt' and 'json' formats
            txt_mwtab_file, txt_validation_log = validate(validation_dict, study_id, analysis_id, 'txt', save_path=save_path)
            json_mwtab_file, json_validation_log = validate(validation_dict, study_id, analysis_id, 'json', save_path=save_path)

            # if both formats are available and parsable, compare the two files
            validation_dict[study_id]["analyses"][analysis_id]["status"]['comparison'] = 'Not Checked'
            if txt_mwtab_file and json_mwtab_file:  # both files passed validation and can be compared
                comparison_list = mwFileStatusWebsite.compare.compare(txt_mwtab_file, json_mwtab_file)

                if comparison_list:
                    comparison_status = 'Inconsistent'
                    error_str = '\n'.join([str(error) for error in comparison_list])
                else:
                    comparison_status = 'Consistent'
                    error_str = ''

                validation_dict[study_id]["analyses"][analysis_id]["status"]['comparison'] = comparison_status
                comparison_log = mwFileStatusWebsite.compare.COMPARISON_LOG.format(
                    str(datetime.now()),
                    mwtab.__version__,
                    MW_REST_URL.format(analysis_id, '...'),
                    study_id,
                    analysis_id,
                    comparison_status
                ) + error_str

                with open(join(logs_path, '{}_comparison.log').format(analysis_id), 'w', encoding='utf-8') as fh:
                    fh.write(comparison_log)

            # save out each files validation log
            with open(join(logs_path, '{}_{}.log'.format(analysis_id, 'txt')), 'w', encoding='utf-8') as fh:
                fh.write(txt_validation_log)
            with open(join(logs_path, '{}_{}.log'.format(analysis_id, 'json')), 'w', encoding='utf-8') as fh:
                fh.write(json_validation_log)

    # export validation status dictionary
    with open(output_file, "w") as fh:
        fh.write(json.dumps(validation_dict, indent=4))

    return validation_dict

