#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

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

DESC_STR = "<div class=\"desc__grid__item\"{0}>{1}</div>"


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


if __name__ == "__main__":

    output_name = "test.html"
    validation_dict = load_validation_json("test2.json")
    num_studies, num_analyses, error_dict = generate_statistics_summary(validation_dict)

    num_errors = list()
    for error_type in error_dict:
        for file_format in error_dict[error_type]:
            num_errors.append(error_dict[error_type][file_format])
    stats_str = STATS_STR.format(num_studies, num_analyses, *num_errors)

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

            print(analysis_id)  # REMOVE
            # analysis_desc_list = []
            # for analysis_key in validation_dict[study_id]["analyses"][analysis_id]["params"]:
            #     analysis_desc_list.append(DESC_STR.format("", analysis_key))
            #     analysis_desc_list.append(
            #         DESC_STR.format(
            #             " style=\"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:calc(100%);\"",
            #             validation_dict[study_id]["analyses"][analysis_id]["params"][analysis_key]
            #         )
            #     )

            badge_list = []
            for format_type in validation_dict[study_id]["analyses"][analysis_id]["status"]:

                badge_list.append(BADGE_STR.format(
                    analysis_id,
                    format_type,
                    MESSAGE_COLOR[validation_dict[study_id]["analyses"][analysis_id]["status"][format_type]],
                    validation_dict[study_id]["analyses"][analysis_id]["status"][format_type]
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

    with open("../"+output_name, "w") as f:
        f.write(INDEX_STR.format(
            str(datetime.now()),
            stats_str,
            file_status_str
        ))
