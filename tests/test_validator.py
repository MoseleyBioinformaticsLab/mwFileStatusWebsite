#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_validator.py
~~~~~~~~~~~~~~~~~

This script contains methods for validating all available mwTab data files, creating log files, and generating a JSON
file containing the validation metadata.
"""
import pytest
import mwFileStatusWebsite
import mwtab
from urllib.request import urlopen
from time import sleep
import pkgutil


FULL_STUDY_ANALYSIS_DICT = pkgutil.get_data(__name__, '/test/study_analysis_dict.json')


# @pytest.mark.parametrize('verbose', [
#     False,
#     True
# ])
# def test_retrieve_mwtab_files(verbose):
#     assert mwFileStatusWebsite.validator.retrieve_mwtab_files(verbose)


# def test_validate_mwtab_files():
#     """Method for testing the ``validate_mwtab_files()`` method in the ``validator`` module.
#
#     :return:
#     """
#     # search for analysis missing `txt` through Metabolomics Workbench REST API
#     txt_missing_ground_truth = set()
#     study_analysis_dict = mwtab.mwrest._pull_study_analysis()
#     for study_id in study_analysis_dict.keys():
#         for analysis_id in study_analysis_dict[study_id]:
#             response = urlopen(mwFileStatusWebsite.validator.MW_REST_URL.format(analysis_id, 'txt'))
#             sleep(1)  # don't piss off Metabolomics Workbench
#             response_str = response.read().decode('utf-8')
#             if response_str:
#                 pass
#             else:
#                 txt_missing_ground_truth.add(analysis_id)
#
#     # search for analysis missing `json` through Metabolomics Workbench REST API
#     json_missing_ground_truth = set()
#     study_analysis_dict = mwtab.mwrest._pull_study_analysis()
#     for study_id in study_analysis_dict.keys():
#         for analysis_id in study_analysis_dict[study_id]:
#             response = urlopen(mwFileStatusWebsite.validator.MW_REST_URL.format(analysis_id, 'json'))
#             sleep(1)  # don't piss off Metabolomics Workbench
#             response_str = response.read().decode('utf-8')
#             if response_str:
#                 pass
#             else:
#                 json_missing_ground_truth.add(analysis_id)
#
#     # test validator method
#     validation_dict = mwFileStatusWebsite.validator.validate_mwtab_files(study_analysis_dict)
#     txt_missing = set()
#     json_missing = set()
#     for study_id in validation_dict.keys():
#         for analysis_id in validation_dict[study_id]['analyses']:
#             if validation_dict[study_id]['analyses'][analysis_id]['status']['txt'] == 'Missing/Blank':
#                 txt_missing.add(analysis_id)
#             if validation_dict[study_id]['analyses'][analysis_id]['status']['json'] == 'Missing/Blank':
#                 json_missing.add(analysis_id)
#
#     # assert number of missing detected by ``validator.py`` is same as ground truth
#     assert txt_missing == txt_missing_ground_truth
#     assert json_missing == json_missing_ground_truth


@pytest.mark.parametrize('input_list', [
    [{'ST000001': 'AN000001'}, 'Passing', 'txt'],
    [{'ST000001': 'AN000001'}, 'Passing', 'json']
])
def test_validate_mwtab_files_hardcoded(input_list):
    """Hardcoded method for testing the ``validate_mwtab_files()`` method in the ``validator`` module.

    :return:
    """
    study_id = list(input_list[0].keys())[0]
    analysis_id = input_list[0][study_id][0]
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_files(input_dict=input_list[0])

    assert validation_dict[study_id]['analyses'][analysis_id]['status'][input_list[2]]

