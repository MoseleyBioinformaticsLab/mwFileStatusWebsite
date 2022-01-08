#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_html.py
~~~~~~~~~~~~~~~~

This script contains methods for generating html pages from validation dictionaries.
"""
import json
from datetime import datetime
import pkgutil


MESSAGE_COLOR = {
    "Passing": "brightgreen",
    "Validation Error": "orange",
    "Parsing Error": "red",
    "Missing/Blank": "lightgrey",
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
INDEX_STR = pkgutil.get_data(__name__, 'templates/index_template.txt').decode('utf-8')
STATS_STR = pkgutil.get_data(__name__, 'templates/statistics_template.txt').decode('utf-8')
HEADER_STR = pkgutil.get_data(__name__, 'templates/header_template.txt').decode('utf-8')
GRID_STR = pkgutil.get_data(__name__, 'templates/grid_template.txt').decode('utf-8')
GRID_ITEM_STR = pkgutil.get_data(__name__, 'templates/grid_item_template.txt').decode('utf-8')
BADGE_STR = pkgutil.get_data(__name__, 'templates/badge_template.txt').decode('utf-8')
DESC_STR = "<div class=\"desc__grid__item\"{0}>{1}</div>"


def load_json(filepath):
    """

    :param filepath:
    :return:
    """
    with open(filepath, "r") as fh:
        json_dict = json.loads(fh.read())
        fh.close()

    return json_dict


def generate_statistics_summary(validation_dict):
    """

    :param validation_dict:
    :return:
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

            for file_format in validation_dict[study_id]["analyses"][analysis_id]["status"]:
                error_num_dict[validation_dict[study_id]["analyses"][analysis_id]["status"][file_format]][file_format] += 1

    return num_studies, num_analyses, error_num_dict


def create_desc(params, tabs="\t"*6):
    desc_items = list()
    for k in params:
        desc_items.append(tabs + DESC_STR.format("", k))
        desc_items.append(tabs + DESC_STR.format(" style=\"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:calc(100%);\"", params.get(k)))

    return "\n".join(desc_items)


def create_html(validation_dict, config_dict, output_filename):
    num_studies, num_analyses, error_dict = generate_statistics_summary(validation_dict)

    num_errors = list()
    for error_type in error_dict:
        for file_format in error_dict[error_type]:
            num_errors.append(error_dict[error_type][file_format])
    stats_str = STATS_STR.format(num_studies, num_analyses, *num_errors, config_dict['owner'], config_dict['repo'])

    # generate file status section
    file_status_list = []
    for study_id in validation_dict:

        if file_status_list:
            file_status_list.append("\t\t\t<br>")

        # Add study header
        #   Adds header line (grid)
        #   Adds study meta data
        height = 1*len(validation_dict[study_id]["params"])
        file_status_list.append(HEADER_STR.format(
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

                badge_list.append(BADGE_STR.format(
                    analysis_id,
                    format_type,
                    MESSAGE_COLOR[validation_dict[study_id]["analyses"][analysis_id]["status"][format_type]],
                    validation_dict[study_id]["analyses"][analysis_id]["status"][format_type],
                    config_dict['owner'],
                    config_dict['repo']
                ))

            grid_item_list.append(GRID_ITEM_STR.format(
                analysis_id,
                MESSAGE_COLOR[LEVEL_TO_MESSAGE[max([
                    MESSAGE_TO_LEVEL[value] for value in validation_dict[study_id]["analyses"][analysis_id]["status"].values()
                ])]],
                "\n".join(badge_list),
                create_desc(validation_dict[study_id]["analyses"][analysis_id]["params"])
            ))

        file_status_list.append(GRID_STR.format("\n".join(grid_item_list)))

    file_status_str = "\n".join(file_status_list)

    with open(output_filename, "w") as f:
        f.write(INDEX_STR.format(
            config_dict['owner'],
            config_dict['repo'],
            str(datetime.now()),
            stats_str,
            file_status_str
        ))


def create_error_dicts(validation_dict, status_str, file_format=None):
    """

    :param validation_dict:
    :return:
    """
    status_dict = dict()

    for study_id in validation_dict:
        for analysis_id in validation_dict[study_id]["analyses"]:
            if not file_format:
                if {status_str} == set(validation_dict[study_id]["analyses"][analysis_id]["status"].values()):
                    status_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                    status_dict[study_id].setdefault("analyses", dict())[analysis_id] =  \
                        validation_dict[study_id]["analyses"][analysis_id]
            elif file_format:
                if status_str in set(validation_dict[study_id]["analyses"][analysis_id]["status"].values()):
                    status_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                    status_dict[study_id].setdefault("analyses", dict())[analysis_id] = \
                        validation_dict[study_id]["analyses"][analysis_id]

    return status_dict
