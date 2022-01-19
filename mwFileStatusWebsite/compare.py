#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare.py
~~~~~~~~~~

This script contains methods comparing two Metabolomics Workbench file in `~mwtab.mwtab.MWTabFile` object and assert
that the files (objects) are the same.
"""
import mwtab
import operator


ITEM_SECTIONS = {
    # "METABOLOMICS WORKBENCH",
    "PROJECT",
    "STUDY",
    "ANALYSIS",
    "SUBJECT",
    "COLLECTION",
    "TREATMENT",
    "SAMPLEPREP",
    "CHROMATOGRAPHY",
    "MS",
    "NM"
}

DATA_BLOCKS = {
    'MS_METABOLITE_DATA',
    'NMR_BINNED_DATA',
    'NMR_METABOLITE_DATA'
}

COMPARISON_LOG = \
"""Comparison Log
{}
mwtab Python Library Version: {}
Source:      {}
Study ID:    {}
Analysis ID: {}
Status:      {}

"""


def compare_blocks(mwtabfile_1, mwtabfile_2):
    """Method for comparing the section headers of two Metabolomics Workbench file in `~mwtab.mwtab.MWTabFile` object
    format. Raises AssertionError if false.

    :param mwtabfile_1: First Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_1: :py:class:`~mwtab.mwtab.MWTabFile`
    :param mwtabfile_2: Second Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_2: :py:class:`~mwtab.mwtab.MWTabFile`
    :return: None
    """
    if not mwtabfile_1.keys() == mwtabfile_2.keys():
        raise AssertionError(
            "mwTab files contain different blocks: \"{}\"".format(
                mwtabfile_1.keys() ^ mwtabfile_2.keys()  # symmetric difference
            )
        )

def compare_block_items(mwtabfile_1, mwtabfile_2):
    """Method for comparing the items (keys and values) present within the sections of two Metabolomics Workbench file
    in `~mwtab.mwtab.MWTabFile` object format.

    :param mwtabfile_1: First Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_1: :py:class:`~mwtab.mwtab.MWTabFile`
    :param mwtabfile_2: Second Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_2: :py:class:`~mwtab.mwtab.MWTabFile`
    :return: List of errors.
    :rtype: list
    """
    error_list = list()

    for section_key in set(mwtabfile_1.keys()) & set(mwtabfile_2.keys()) & ITEM_SECTIONS:
        if mwtabfile_1[section_key].items() ^ mwtabfile_2[section_key].items():
            error_list.append(
                AssertionError(
                    "Sections \"{}\" contain missmatched items: {}".format(
                        section_key,
                        mwtabfile_1[section_key].items() ^ mwtabfile_2[section_key].items()
                    )
                )
            )

    return error_list


def compare_subject_sample_factors(mwtabfile_1, mwtabfile_2):
    """Method for comparing the items (keys and values) present within the sections of two Metabolomics Workbench file
    in `~mwtab.mwtab.MWTabFile` object format.

    :param mwtabfile_1: First Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_1: :py:class:`~mwtab.mwtab.MWTabFile`
    :param mwtabfile_2: Second Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_2: :py:class:`~mwtab.mwtab.MWTabFile`
    :return: None
    """
    new_mwtabfile_1_SSF_list = sorted(mwtabfile_1['SUBJECT_SAMPLE_FACTORS'], key=operator.itemgetter('Sample ID'))
    new_mwtabfile_2_SSF_list = sorted(mwtabfile_2['SUBJECT_SAMPLE_FACTORS'], key=operator.itemgetter('Sample ID'))

    if new_mwtabfile_1_SSF_list != new_mwtabfile_2_SSF_list:
        raise AssertionError("mwTab files contain different 'SUBJECT_SAMPLE_FACTORS' sections.")


def compare_data(mwtabfile_1, mwtabfile_2):
    """Method for comparing "_DATA" blocks present within two Metabolomics Workbench file in `~mwtab.mwtab.MWTabFile`
    object format.

    :param mwtabfile_1: First Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_1: :py:class:`~mwtab.mwtab.MWTabFile`
    :param mwtabfile_2: Second Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_2: :py:class:`~mwtab.mwtab.MWTabFile`
    :return: List of errors.
    :rtype: list
    """
    data_section = set(mwtabfile_1.keys()) & set(mwtabfile_2.keys()) & DATA_BLOCKS

    # data block is not consistently present across files
    if not data_section or type(data_section) != set:
        return [AssertionError("Unable to find '_DATA' block in given files.")]

    else:
        data_section = list(data_section)[0]
        error_list = list()
        subsections = set(mwtabfile_1[data_section].keys()) & set(mwtabfile_2[data_section].keys())

        if mwtabfile_1[data_section].keys() != mwtabfile_2[data_section].keys():
            error_list.append(AssertionError("'_DATA' blocks do not contain the same subsections: {}".format(
                set(mwtabfile_1[data_section].keys()) ^ set(mwtabfile_2[data_section].keys())
            )))

        # compare "Units"
        if 'Units' in subsections:
            if mwtabfile_1[data_section]['Units'] != mwtabfile_2[data_section]['Units']:
                error_list.append(AssertionError("'Units' section of '{}' block do not match.".format(data_section)))

        # compare "Metabolites"
        if 'Metabolites' in subsections:
            try:
                new_mwtabfile_1_metabolites_list = sorted(mwtabfile_1[data_section]['Metabolites'],
                                                          key=operator.itemgetter('Metabolite'))
                new_mwtabfile_2_metabolites_list = sorted(mwtabfile_2[data_section]['Metabolites'],
                                                          key=operator.itemgetter('Metabolite'))
                if new_mwtabfile_1_metabolites_list != new_mwtabfile_2_metabolites_list:
                    error_list.append(AssertionError("'Metabolites' section of '{}' block do not match.".format(data_section)))
            except Exception as e:
                error_list.append(e)

        # compare "Data"
        if 'Data' in subsections:
            try:
                new_mwtabfile_1_data_list = sorted(mwtabfile_1[data_section]['Data'],
                                                          key=operator.itemgetter('Metabolite'))
                new_mwtabfile_2_data_list = sorted(mwtabfile_2[data_section]['Data'],
                                                          key=operator.itemgetter('Metabolite'))
                if new_mwtabfile_1_data_list != new_mwtabfile_2_data_list:
                    error_list.append(AssertionError("'Data' section of '{}' block do not match.".format(data_section)))
            except Exception as e:
                error_list.append(e)

        return error_list


def compare(mwtabfile_1, mwtabfile_2):
    """Method for comparing two Metabolomics Workbench file in `~mwtab.mwtab.MWTabFile` object format to assert that
    they are the same. Raises AssertionError if false.

    :param mwtabfile_1: First Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_1: :py:class:`~mwtab.mwtab.MWTabFile`
    :param mwtabfile_2: Second Metabolomics Workbench file in mwtab format to be compared.
    :type mwtabfile_2: :py:class:`~mwtab.mwtab.MWTabFile`
    :return: Log of assertion errors.
    """
    error_list = list()

    # compare files to assert they have the same section headings.
    try:
        compare_blocks(mwtabfile_1, mwtabfile_2)
    except Exception as e:
        error_list.append(e)

    # compare files to assert they have the same items in each  appropriate block (e.g. PROJECT, STUDY, etc.).
    error_list.extend(compare_block_items(mwtabfile_1, mwtabfile_2))  # no issue if compare_block_keys() returns a null list.

    # check that the SUBJECT_SAMPLE_FACTORS sections match
    try:
        compare_subject_sample_factors(mwtabfile_1, mwtabfile_2)
    except Exception as e:
        error_list.append(e)

    error_list.extend(compare_data(mwtabfile_1, mwtabfile_2))

    return error_list
