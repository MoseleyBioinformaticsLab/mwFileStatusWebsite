#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
constructor.py
~~~~~~~~~~~~~~~~

This script contains methods for generating HTML pages from validation dictionaries.
"""
import json
from datetime import datetime
import pkgutil


MESSAGE_COLOR = {
    "Passing": "brightgreen",
    "Warnings Only": "yellow",
    "Validation Error": "orange",
    "Parsing Error": "red",
    "Missing/Blank": "brightred",
    'Consistent': 'brightgreen',
    'Inconsistent': 'orange',
    'Not Checked': 'lightgrey'
}
MESSAGE_TO_LEVEL = {
    "Passing": 0,
    "Warnings Only": 1,
    "Validation Error": 2,
    "Parsing Error": 3,
    "Missing/Blank": 4,
}
LEVEL_TO_MESSAGE = {
    MESSAGE_TO_LEVEL[k]: k for k in MESSAGE_TO_LEVEL
}
# load in all the necessary HTML templates
INDEX_HEADER_TEMPLATE = pkgutil.get_data(__name__, 'templates/index_header_template.txt').decode('utf-8')
INDEX_TEMPLATE = pkgutil.get_data(__name__, 'templates/index_template.txt').decode('utf-8')
STATUS_STATS_TEMPLATE = pkgutil.get_data(__name__, 'templates/statistics_template_status.txt').decode('utf-8')
ISSUES_STATS_TEMPLATE = pkgutil.get_data(__name__, 'templates/statistics_template_issues.txt').decode('utf-8')
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
    :return: Tuple containing the number of validated studies, number of validated analyses, the dictionary
    containing the validation data (eg. number Passing, number with Validation Errors, etc.), and the dicitonary 
    containing validation issues.
    :rtype: tuple
    """
    num_studies = 0
    num_analyses = 0
    error_num_dict = {
        key: {"txt": 0, "json": 0} for key in ["Passing", "Warnings Only", "Validation Error", "Parsing Error", "Missing/Blank"]
    }
    issue_types = ["value", "consistency", "format"]
    issue_num_dict = {
        key: {"txt": 0, "json": 0} for key in issue_types
    }

    for study_id in validation_dict:
        num_studies += 1

        for analysis_id, analysis_dict in validation_dict[study_id]["analyses"].items():
            num_analyses += 1

            for file_format in ('txt', 'json'):
                error_num_dict[analysis_dict["status"][file_format]][file_format] += 1
                for issue_type in issue_types:
                    if analysis_dict["issues"][file_format][issue_type]:
                        issue_num_dict[issue_type][file_format] += 1

    return num_studies, num_analyses, error_num_dict, issue_num_dict


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
    :rtype: str
    """
    desc_items = list()
    for k in params:
        desc_items.append(tabs + DESC_TEMPLATE.format("", k))
        desc_items.append(tabs + DESC_TEMPLATE.format(" style=\"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:calc(100%);\"", params.get(k)))

    return "\n".join(desc_items)


def create_html(validation_dict, owner, repo, output_filename):
    """Creates and saves HTML file based on given validation and config dictionaries.

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param owner: The GitHub account name that owns the repo where the html files will be committed to. Used to build links between html pages.
    :type owner: str
    :param repo: The name of the repo where the html files will be committed to. Used to build links between html pages.
    :type repo: str
    :param output_filename: Filename of HTML file to be created.
    :type output_filename: str
    :return: None
    """
    with open(output_filename, "w", encoding='utf-8') as fh:

        #####################################
        # write the HTML header information #
        #####################################
        fh.write(INDEX_HEADER_TEMPLATE.format(
            owner,
            repo,
            str(datetime.now()),
        ))

        #####################################################
        # collect and write validation and comparison stats #
        #####################################################
        # collect general statistics for the run (number of available studies and analyses).
        num_studies, num_analyses, error_dict, issue_dict = generate_validation_stats_summary(validation_dict)

        # Fill out the statistics_template and comparison_stats_template.
        num_errors = list()
        for error_type in error_dict:
            for file_format in error_dict[error_type]:
                num_errors.append(error_dict[error_type][file_format])
        issue_errors = []
        for issue_type in issue_dict:
            for file_format in issue_dict[issue_type]:
                issue_errors.append(issue_dict[issue_type][file_format])

        # writes the validation and comparison stats sections to the HTML file
        fh.write(STATUS_STATS_TEMPLATE.format(num_studies, num_analyses, *num_errors, owner, repo))
        fh.write(ISSUES_STATS_TEMPLATE.format(*issue_errors, owner, repo))
        fh.write(COMP_STATS_TEMPLATE.format(*generate_comparison_stats_summary(validation_dict)))

        ################################
        # generate file status section #
        ################################
        # file_status_list = []
        num_of_analyses = 0
        for i, study_id in enumerate(validation_dict):
            # Add study header
            # Adds header line (grid)
            # Adds study meta data
            height = 1*len(validation_dict[study_id]["params"])
            study_description = HEADER_TEMPLATE.format(
                study_id,
                validation_dict[study_id]["params"].get("STUDY_TITLE"),
                validation_dict[study_id]["params"].get("INSTITUTE"),
                validation_dict[study_id]["params"].get("LAST_NAME"),
                validation_dict[study_id]["params"].get("FIRST_NAME"),
                " style=\"height:" + str(height) + "em;max-height:" + str(height) + "\"",
                create_desc(validation_dict[study_id]["params"]),
                i
            )
            fh.write(study_description)

            grid_item_list = []
            for analysis_id in validation_dict[study_id]["analyses"]:
                num_of_analyses += 1

                badge_list = []
                for format_type in validation_dict[study_id]["analyses"][analysis_id]["status"]:

                    badge_list.append(BADGE_TEMPLATE.format(
                        analysis_id,
                        format_type,
                        MESSAGE_COLOR[validation_dict[study_id]["analyses"][analysis_id]["status"][format_type]],
                        validation_dict[study_id]["analyses"][analysis_id]["status"][format_type],
                        owner,
                        repo
                    ))

                # adds the colored analysis button
                grid_item_list.append(GRID_ITEM_TEMPLATE.format(
                    analysis_id,
                    MESSAGE_COLOR[LEVEL_TO_MESSAGE[max([
                        MESSAGE_TO_LEVEL[value] for value in validation_dict[study_id]["analyses"][analysis_id]["status"].values() if value in MESSAGE_TO_LEVEL.keys()
                    ])]],
                    "\n".join(badge_list),
                    create_desc(validation_dict[study_id]["analyses"][analysis_id]["params"]),
                    num_of_analyses
                ))

            fh.write(GRID_TEMPLATE.format("\n".join(grid_item_list)))

            fh.write("\t\t\t<br>")

        # close file
        fh.write("\t\t</div>\n\t</body>\n</html>\n")


def filter_analyses_by_status(validation_dict, status_str, match_all_formats = False):
    """Method for creating a dictionary containing the validation status and additional parameters of analyses with
    indicated validation status.

    :param validation_dict: Structured dictionary containing analyses statuses and other study information.
    :type validation_dict: dict
    :param status_str: Analysis validation status to be searched for.
    :type status_str: str
    :param match_all_formats: Whether all file formats must have the indicated status_str or just one.
    :type match_all_formats: bool
    :return: Structured dictionary containing analyses statuses and other study information for analyses with indicated
    validation status.
    :rtype: dict
    """
    status_dict = dict()

    for study_id in validation_dict:
        for analysis_id, analysis_dict in validation_dict[study_id]["analyses"].items():
            file_format_status_set = set(analysis_dict["status"].values())
            if (match_all_formats and {status_str} == file_format_status_set) or \
               (not match_all_formats and status_str in file_format_status_set):
                status_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                status_dict[study_id].setdefault("analyses", dict())[analysis_id] = analysis_dict

    return status_dict


def filter_analyses_by_issues(validation_dict, issues_str, match_all_formats = False):
    """Method for creating a dictionary containing the validation issues and additional parameters of analyses with
    indicated validation issues.

    :param validation_dict: Structured dictionary containing analyses issues and other study information.
    :type validation_dict: dict
    :param issues_str: Analysis validation issues to be searched for. Should only ever be 'value', consistency', or 'format'.
    :type issues_str: str
    :param match_all_formats: Whether all file formats must have the indicated status_str or just one.
    :type match_all_formats: bool
    :return: Structured dictionary containing analyses statuses and other study information for analyses with indicated
    validation issues.
    :rtype: dict
    """
    issues_dict = dict()

    for study_id in validation_dict:
        for analysis_id, analysis_dict in validation_dict[study_id]["analyses"].items():
            file_format_issues = [analysis_dict['issues']['json'][issues_str], analysis_dict['issues']['txt'][issues_str]]
            if (match_all_formats and all(file_format_issues)) or \
               (not match_all_formats and any(file_format_issues)):
                issues_dict.setdefault(study_id, dict()).setdefault("params", validation_dict[study_id]["params"])
                issues_dict[study_id].setdefault("analyses", dict())[analysis_id] = analysis_dict

    return issues_dict






