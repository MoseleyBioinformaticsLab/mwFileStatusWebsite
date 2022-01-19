#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_compare.py
~~~~~~~~~~~~~~~

This script contains methods comparing two Metabolomics Workbench file in `~mwtab.mwtab.MWTabFile` object and assert
that the files (objects) are the same.
"""
import pytest
import mwFileStatusWebsite
import mwtab
from urllib.request import urlopen
from time import sleep
import pkgutil
from collections import OrderedDict


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    ({"a": {"b": 1}}, {"a": {"b": 1}}, False),  # same blocks, same items
    ({"a": {"b": 1}}, {"a": {"c": 1}}, False),  # same blocks, different item blocks
    ({"a": {"b": 1}}, {"b": {"b": 1}}, True),  # different blocks
    ({"a": {"b": 1}}, {"a": {"b": 1}, "c": {"b": 1}}, True), # one file has an additional block
    ({"a": {"b": 1}}, {}, True),  # one file is null
])
def test_compare_blocks(mwtabfile_1, mwtabfile_2, error):
    try:
        mwFileStatusWebsite.compare.compare_blocks(mwtabfile_1, mwtabfile_2)
        if error:  # test should have raise an error
            assert False
    except Exception as e:
        if not error:
            assert False


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"b": 1}}, False),  # same blocks, same items
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"c": 1}}, True),  # same blocks, different item blocks
    ({"PROJECT": {"b": 1}}, {"PROJECT": {}}, True),  # same blocks, one block is null
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"b": 1}, "STUDY": {"a": 1}}, False),  # different blocks, same items in mutual blocks
])
def test_compare_block_items(mwtabfile_1, mwtabfile_2, error):
    errors = mwFileStatusWebsite.compare.compare_block_items(mwtabfile_1, mwtabfile_2)
    if bool(errors) != error:
        assert False


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    # same SSF section
    (
        {'SUBJECT_SAMPLE_FACTORS':[
            OrderedDict([('Subject ID', '-'), ('Sample ID', '1'), ('Factors', {'Factor1': 'Blah'})])
        ]},
        {'SUBJECT_SAMPLE_FACTORS': [
            OrderedDict([('Subject ID', '-'), ('Sample ID', '1'), ('Factors', {'Factor1': 'Blah'})])
        ]},
        False
    ),
    # different 'Sample ID'
    (
        {'SUBJECT_SAMPLE_FACTORS': [
            OrderedDict([('Subject ID', '-'), ('Sample ID', '1'), ('Factors', {'Factor1': 'Blah'})])
        ]},
        {'SUBJECT_SAMPLE_FACTORS': [
            OrderedDict([('Subject ID', '-'), ('Sample ID', '2'), ('Factors', {'Factor1': 'Blah'})])
        ]},
        True
    ),
    # different factor values
    (
        {'SUBJECT_SAMPLE_FACTORS': [
            OrderedDict([('Subject ID', '-'), ('Sample ID', '1'), ('Factors', {'Factor1': 'Blah'})])
        ]},
        {'SUBJECT_SAMPLE_FACTORS': [
            OrderedDict([('Subject ID', '-'), ('Sample ID', '1'), ('Factors', {'Factor1': 'Meh'})])
        ]},
        True
    )
])
def test_compare_block_items(mwtabfile_1, mwtabfile_2, error):
    try:
        mwFileStatusWebsite.compare.compare_subject_sample_factors(mwtabfile_1, mwtabfile_2)
        if error:  # test should have raise an error
            assert False
    except Exception as e:
        if not error:
            assert False


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    # same "_DATA" section
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'),('Value_1', 'Test')])],
        }},
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        False
    ),

    # different "_DATA" sections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MNMR_BINNED_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        True
    ),

    # different "Units" subsections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MNMR_BINNED_DATA': {
            'Units': 'test2',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        True
    ),

    # different "Data" sections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MNMR_BINNED_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test2'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        True
    ),

    # different "Metabolites" sections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MNMR_BINNED_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test2'), ('Value_1', 'Test')])],
        }},
        True
    ),
])
def test_compare_data(mwtabfile_1, mwtabfile_2, error):
    errors = mwFileStatusWebsite.compare.compare_data(mwtabfile_1, mwtabfile_2)

    if errors and not error:
        assert False

    if not errors and error:
        assert False
