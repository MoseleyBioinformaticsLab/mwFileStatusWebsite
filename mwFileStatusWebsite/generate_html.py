#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_html.py
~~~~~~~~~~~~~~~~

This script contains methods for generating HTML pages from validation dictionaries.
"""
import json
from datetime import datetime
import pkgutil


MESSAGE_COLOR = {
    "Passing": "brightgreen",
    "Validation Error": "orange",
    "Parsing Error": "red",
    "Missing/Blank": "lightgrey",
    'Consistent': 'brightgreen',
    'Inconsistent': 'orange',
    'Not Checked': 'lightgrey'
}
MESSAGE_TO_LEVEL = {
    "Passing": 0,
    "Validation Error": 1,
    "Parsing Error": 2,
    "Missing/Blank": 3,
}
LEVEL_TO_MESSAGE = {
    MESSAGE_TO_LEVEL[k]: k for k in MESSAGE_TO_LEVEL
}
# load in all the necessary HTML templates
INDEX_TEMPLATE = pkgutil.get_data(__name__, 'templates/index_template.txt').decode('utf-8')
VAL_STATS_TEMPLATE = pkgutil.get_data(__name__, 'templates/statistics_template.txt').decode('utf-8')
COMP_STATS_TEMPLATE = pkgutil.get_data(__name__, 'templates/comparison_stats_template.txt').decode('utf-8')
HEADER_TEMPLATE = pkgutil.get_data(__name__, 'templates/header_template.txt').decode('utf-8')
GRID_TEMPLATE = pkgutil.get_data(__name__, 'templates/grid_template.txt').decode('utf-8')
GRID_ITEM_TEMPLATE = pkgutil.get_data(__name__, 'templates/grid_item_template.txt').decode('utf-8')
BADGE_TEMPLATE = pkgutil.get_data(__name__, 'templates/badge_template.txt').decode('utf-8')
DESC_TEMPLATE = "<div class=\"desc__grid__item\"{0}>{1}</div>"


def load_json(filepath):
    """Help function for loading in JSON data files.

    :param filepath: Path to JSON file to be loaded.
    :type filepath: str
    :return: JSON dictionary object.
    :rtype: dict
    """
    with open(filepath, "r") as fh:
        json_dict = json.loads(fh.read())
        fh.close()

    return json_dict


def generate_validation_stats_summary(validation_dict):
    """Method for generating the statistics to filling the HTML template with the current Metabolomics Workbench mwTab
    files validation data.

    :param validation_dict: Dictionary object containing the validation statuses for all validated mwTab data files.
    :type validation_dict: dict
    :return: Tuple containing the number of validated studies, number of validated analyses, and the dictionary
    containing the validation data (eg. number Passing, number with Validation Errors, etc.).
    :rtype: tuple
    """
    num_studies = 0
    num_analyses = 0
    error_num_dict = {
        key: {"txt": 0, "json": 0} for key in [
            "Passing", "Parsing Error", "Validation Error", "Missing/Blank"
        ]
    }

    for study_id in validation_dict:
        num_studies += 1

        for analysis_id in validation_dict[study_id]["analyses"]:
            num_analyses += 1

            for file_format in ('txt', 'json'):
                error_num_dict[validation_dict[study_id]["analyses"][analysis_id]["status"][file_format]][file_format] += 1

    return num_studies, num_analyses, error_num_dict


def generate_comparison_stats_summary(validation_dict):
    """Method for generating the statistics to filling the HTML template with the current Metabolomics Workbench mwTab
    files comparison data.

    :param validation_dict: Dictionary object containing the validation statuses for all validated mwTab data files.
    :type validation_dict: dict
    :return: Tuple containing the number of validated studies, number of validated analyses, and the dictionary
    containing the validation data (eg. number Passing, number with Validation Errors, etc.).
    :rtype: tuple
    """
    count_dict = {
        'Consistent': 0,
        'Inconsistent': 0,
        'Not Checked': 0,
    }

    for study_id in validation_dict:
        for analysis_id in validation_dict[study_id]['analyses']:
            count_dict[validation_dict[study_id]['analyses'][analysis_id]['status']['comparison']] += 1

    return count_dict['Consistent'], count_dict['Inconsistent'], count_dict['Not Checked']


def create_desc(params, tabs="\t"*6):
    """Method for parsing out STUDY or ANALYSIS description items from the generated validation nested dictionary and
    returning a formatted string.

    :param params: Nested validation dictionary or section of nested validation dictionary.
    :type params: dict
    :param tabs: White spacing for tabs.
    :type tabs: str
    :return: String containing formatted
    """
    desc_items = list()
    for k in params:
        desc_items.append(tabs + DESC_TEMPLATE.format("", k))
        desc_items.append(tabs + DESC_TEMPLATE.format(" style=\"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:calc(100%);\"", params.get(k)))

    return "\n".join(desc_items)


def create_html(validation_dict, config_dict, output_filename):
    """Method for generating the text for the HTML files for the website.

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param config_dict: Dictionary containing GitHub repository information.
    :type config_dict: dict
    :param output_filename: Filename of HTML file to be created.
    :type output_filename: str
    :return: None
    """
    # collect general statistics for the run (number of available studies and analyses).
    num_studies, num_analyses, error_dict = generate_validation_stats_summary(validation_dict)

    # Fill out the statistics_template and comparison_stats_template.
    num_errors = list()
    for error_type in error_dict:
        for file_format in error_dict[error_type]:
            num_errors.append(error_dict[error_type][file_format])
    val_stats_str = VAL_STATS_TEMPLATE.format(num_studies, num_analyses, *num_errors, config_dict['owner'], config_dict['repo'])
    comp_stats_str = COMP_STATS_TEMPLATE.format(*generate_comparison_stats_summary(validation_dict))

    # generate file status section
    file_status_list = []
    for study_id in validation_dict:

        # Add space between grid items
        if file_status_list:
            file_status_list.append("\t\t\t<br>")

        # Add study header
        # Adds header line (grid)
        # Adds study meta data
        height = 1*len(validation_dict[study_id]["params"])
        file_status_list.append(HEADER_TEMPLATE.format(
            study_id,
            validation_dict[study_id]["params"].get("STUDY_TITLE"),
            validation_dict[study_id]["params"].get("INSTITUTE"),
            validation_dict[study_id]["params"].get("LAST_NAME"),
            validation_dict[study_id]["params"].get("FIRST_NAME"),
            " style=\"height:" + str(height) + "em;max-height:" + str(height) + "\"",
            create_desc(validation_dict[study_id]["params"])
        ))

        grid_item_list = []
        for analysis_id in validation_dict[study_id]["analyses"]:

            badge_list = []
            for format_type in validation_dict[study_id]["analyses"][analysis_id]["status"]:

                badge_list.append(BADGE_TEMPLATE.format(
                    analysis_id,
                    format_type,
                    MESSAGE_COLOR[validation_dict[study_id]["analyses"][analysis_id]["status"][format_type]],
                    validation_dict[study_id]["analyses"][analysis_id]["status"][format_type],
                    config_dict['owner'],
                    config_dict['repo']
                ))

            # adds the colored analysis button
            grid_item_list.append(GRID_ITEM_TEMPLATE.format(
                analysis_id,
                MESSAGE_COLOR[LEVEL_TO_MESSAGE[max([
                    MESSAGE_TO_LEVEL[value] for value in validation_dict[study_id]["analyses"][analysis_id]["status"].values() if value in MESSAGE_TO_LEVEL.keys()
                ])]],
                "\n".join(badge_list),
                create_desc(validation_dict[study_id]["analyses"][analysis_id]["params"])
            ))

        file_status_list.append(GRID_TEMPLATE.format("\n".join(grid_item_list)))

    file_status_str = "\n".join(file_status_list)

    with open(output_filename, "w") as f:
        f.write(INDEX_TEMPLATE.format(
            config_dict['owner'],
            config_dict['repo'],
            str(datetime.now()),
            val_stats_str,
            comp_stats_str,
            file_status_str
        ))


def create_error_dicts(validation_dict, status_str, file_format=None):
    """Method for creating a dictionary containing the validation status and additional parameters of analyses with
    indicated validation status.

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param status_str: Analysis validation status to be searched for.
    :type status_str: str
    :param file_format: Indicates which file format to be searched (if only one).
    :type file_format: str or bool
    :return: Structured dictionary containing analyses statuses and other study information for analyses with indicated
    validation status.
    :rtype: dict
    """
    status_dict = dict()

    for study_id in validation_dict:
        for analysis_id in validation_dict[study_id]["analyses"]:

            # both file formats have the same validation status
            if not file_format:
                file_format_status_set = {validation_dict[study_id]["analyses"][analysis_id]["status"]['json'],
                                          validation_dict[study_id]["analyses"][analysis_id]["status"]['txt']}
                if {status_str} == file_format_status_set:
                    status_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                    status_dict[study_id].setdefault("analyses", dict())[analysis_id] = \
                        validation_dict[study_id]["analyses"][analysis_id]

            # TODO: Allow specifying which file format to be checked

            # only one file format has a given status
            else:
                if status_str in set(validation_dict[study_id]["analyses"][analysis_id]["status"].values()):
                    status_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                    status_dict[study_id].setdefault("analyses", dict())[analysis_id] =  \
                        validation_dict[study_id]["analyses"][analysis_id]

    return status_dict
