#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
~~~~~~~

This script is the main module for validating Metabolomics Workbench mwTab files.

The script attempts
"""
import mwtab
import json


MW_REST_URL = "https://www.metabolomicsworkbench.org/rest/study/analysis_id/{}/mwtab/{}"
BADGE_URL = "https://img.shields.io/static/v1?label={}&message={}&color={}&link={}&link={}"
REPO_PATH = "https://github.com/cdpowell/test-repo/blob/master/docs/validation_logs/{}.log"


def validate_mw_files():
    """

    :return:
    """
    try:
        mapping = mwtab.mwrest.pull_study_analysis()

        print("{} studies found".format(len(mapping)))
        print("{} analyses found".format(sum([len(mapping[k]) for k in mapping])))

        # setup some variables for collecting validation statuses
        validation_dict = {study_id: dict() for study_id in mapping.keys()}

        study_ids = sorted(mapping.keys())
        for study_id in study_ids:
            print(study_id)

            analysis_ids = sorted(mapping[study_id])
            for analysis_id in analysis_ids:
                print("\t", analysis_id)

                for file_format in ("txt", "json"):

                    try:
                        mwtabfile = next(mwtab.read_files(MW_REST_URL.format(analysis_id, file_format)))
                        _, error_log_str = mwtab.validate_file(mwtabfile, metabolites=False)

                        if not error_log_str:
                            validation_dict[study_id].setdefault(analysis_id, list()).append([
                                file_format,
                                "Passing",
                                "lightgreen",
                                MW_REST_URL.format(analysis_id, file_format),
                                REPO_PATH.format(analysis_id)
                            ])

                        else:
                            validation_dict[study_id].setdefault(analysis_id, list()).append([
                                file_format,
                                "Validation Error",
                                "orange",
                                MW_REST_URL.format(analysis_id, file_format),
                                REPO_PATH.format(analysis_id)
                            ])

                            with open("docs/validation_logs/{}_{}.log".format(analysis_id, file_format), "w") as fh:
                                fh.write(error_log_str)

                    except Exception as e:

                        if type(e) in (TypeError, IndexError):
                            validation_dict[study_id].setdefault(analysis_id, list()).append([
                                file_format,
                                "Parsing Error",
                                "red",
                                MW_REST_URL.format(analysis_id, file_format),
                                REPO_PATH.format(analysis_id)
                            ])
                        else:
                            validation_dict[study_id].setdefault(analysis_id, list()).append([
                                file_format,
                                "Missing/Blank",
                                "lightgrey",
                                MW_REST_URL.format(analysis_id, file_format),
                                REPO_PATH.format(analysis_id)
                            ])

                        with open("docs/validation_logs/{}_{}.log".format(analysis_id, file_format), "w") as fh:
                            fh.write(str(e))

        # generate index.html main page

    except Exception as e:
        # cannot access Metabolomics Workbench REST server
        print(e)

    # export validation status dictionary
    with open("validation.json", "w") as fh:
        fh.write(json.dumps(validation_dict))

    return validation_dict


def create_badge_url(label, message, color, link_left, link_right):
    """Method for creating

    :param label:
    :param message:
    :param color:
    :param link_left:
    :param link_right:
    :return:
    """
    return BADGE_URL.format(label, message, color, link_left, link_right)


if __name__ == "__main__":

    # validate_mw_files()
    with open("docs/templates/analysis_template.html", "r") as fh:
        analysis_template = fh.read()

    with open("validation.json", "r") as fh:
        validation_dict = json.loads(fh.read())

    validation_str = ""
    for study_id in validation_dict:

        validation_str += "<h2>{}</h2>\n".format(study_id)

        for analysis_id in validation_dict[study_id]:
            validation_str += analysis_template.format(
                analysis_id,
                create_badge_url(*validation_dict[study_id][analysis_id][0]),
                create_badge_url(*validation_dict[study_id][analysis_id][1]),
            )

    with open("docs/templates/template.html", "r") as fh:
        index_str = fh.read()

    with open("index.html", "w") as fh:
        fh.write(index_str.format(validation_str))
