#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

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
with open("../docs/templates/index_template.txt", "r") as f:
    INDEX_STR = f.read()
with open("../docs/templates/statistics_template.txt", "r") as f:
    STATS_STR = f.read()
    # study_id, description
with open("../docs/templates/header_template.txt", "r") as f:
    HEADER_STR = f.read()
with open("../docs/templates/grid_template.txt", "r") as f:
    GRID_STR = f.read()
with open("../docs/templates/grid_item_template.txt", "r") as f:
    GRID_ITEM_STR = f.read()
    # analysis_id, file_format, badge_color, badge_message
with open("../docs/templates/badge_template.txt", "r") as f:
    BADGE_STR = f.read()


"""
{
    study_id: {
        analysis_id: [
            ["txt", message],
            ["json", message]
        ],
        ...
    },
    ...
}
"""

example = {
    "ST000001": {
        "AN000001": [
            ["txt", "Passing"],
            ["json", "Passing"]
        ],
        "AN000002": [
            ["txt", "Missing/Blank"],
            ["json", "Passing"]
        ]
    },
    "ST000002": {
        "AN000003": [
            ["txt", "Validation Error"],
            ["json", "Parsing Error"]
        ],
        "AN000004": [
            ["txt", "Missing/Blank"],
            ["json", "Passing"]
        ]
    }
}


def load_validation_json(filepath):
    """

    :param filepath:
    :return:
    """
    with open(filepath, "r") as fh:
        validation_dict = json.loads(fh.read())
        fh.close()

    return validation_dict


def generate_statistics_summary(validation_dict):
    """

    :param validation_dict:
    :return:
    """
    num_studies = 0
    num_analyses = 0
    num_passing = 0
    num_error = 0
    num_missing = 0
    num_parsing = 0
    num_validation = 0

    for study_id in validation_dict:

        num_studies += 1

        for analysis_id in validation_dict[study_id]:

            num_analyses += 1

            for file_format in validation_dict[study_id][analysis_id]:

                if file_format[1] == "Passing":

                    num_passing += 1

                else:

                    num_error += 1

                    if file_format[1] == "Missing/Blank":

                        num_missing += 1

                    elif file_format[1] == "Parsing Error":

                        num_parsing += 1

                    elif file_format[1] == "Validation Error":

                        num_validation += 1

    return num_studies, num_analyses, num_passing, num_error, num_missing, num_parsing, num_validation


if __name__ == "__main__":

    validation_dict = load_validation_json("tmp.json")

    stats_str = STATS_STR.format(*generate_statistics_summary(validation_dict))


    # generate file status section
    file_status_list = []
    for study_id in validation_dict:

        if file_status_list:
            file_status_list.append("<br>")

        # add study header
        file_status_list.append(HEADER_STR.format(study_id, ""))

        grid_item_list = []
        for analysis_id in validation_dict[study_id]:

            badge_list = []

            for params in validation_dict[study_id][analysis_id]:

                badge_list.append(BADGE_STR.format(analysis_id, params[0], MESSAGE_COLOR[params[1]], params[1]))

            grid_item_list.append(GRID_ITEM_STR.format(
                MESSAGE_COLOR[LEVEL_TO_MESSAGE[max([MESSAGE_TO_LEVEL[params[1]] for params in validation_dict[study_id][analysis_id]])]],
                analysis_id,
                "\n".join(badge_list)
            ))

        file_status_list.append(GRID_STR.format("\n".join(grid_item_list)))

    file_status_str = "\n".join(file_status_list)

    with open("../index.html", "w") as f:
        f.write(INDEX_STR.format(
            "NOW",
            stats_str,
            file_status_str
        ))
