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
from collections import OrderedDict
from contextlib import nullcontext as does_not_raise


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    ({"a": {"b": 1}}, {"a": {"b": 1}}, False),  # same blocks, same items
    ({"a": {"b": 1}}, {"a": {"c": 1}}, False),  # same blocks, different item blocks
    ({"a": {"b": 1}}, {"b": {"b": 1}}, True),  # different blocks
    ({"a": {"b": 1}}, {"a": {"b": 1}, "c": {"b": 1}}, True), # one file has an additional block
    ({"a": {"b": 1}}, {}, True),  # one file is null
])
def test_compare_blocks(mwtabfile_1, mwtabfile_2, error):
    if error:
        with pytest.raises(AssertionError):
            mwFileStatusWebsite.compare.compare_blocks(mwtabfile_1, mwtabfile_2)
    else:
        with does_not_raise():
            mwFileStatusWebsite.compare.compare_blocks(mwtabfile_1, mwtabfile_2)


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error', [
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"b": 1}}, False),  # same blocks, same items
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"c": 1}}, True),  # same blocks, different item blocks
    ({"PROJECT": {"b": 1}}, {"PROJECT": {}}, True),  # same blocks, one block is null
    ({"PROJECT": {"b": 1}}, {"PROJECT": {"b": 1}, "STUDY": {"a": 1}}, False),  # different blocks, same items in mutual blocks
])
def test_compare_block_items(mwtabfile_1, mwtabfile_2, error):
    errors = mwFileStatusWebsite.compare.compare_block_items(mwtabfile_1, mwtabfile_2)
    if error:
        assert len(errors) == 1
    else:
        assert len(errors) == 0


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
def test_compare_subject_sample_factors(mwtabfile_1, mwtabfile_2, error):
    if error:
        with pytest.raises(AssertionError):
            mwFileStatusWebsite.compare.compare_subject_sample_factors(mwtabfile_1, mwtabfile_2)
    else:
        with does_not_raise():
            mwFileStatusWebsite.compare.compare_subject_sample_factors(mwtabfile_1, mwtabfile_2)


@pytest.mark.parametrize('mwtabfile_1, mwtabfile_2, error_msg', [
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
        {'NMR_BINNED_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        "Unable to find '_DATA' block in given files."
    ),
    
    # different keys sections
    (
        {'MS_METABOLITE_DATA': {
            'Units1': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MS_METABOLITE_DATA': {
            'Units2': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        "'_DATA' blocks do not contain the same subsections:"
    ),

    # different "Units" subsections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MS_METABOLITE_DATA': {
            'Units': 'test2',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        "'Units' section of 'MS_METABOLITE_DATA' block do not match."
    ),

    # different "Data" sections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test2'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        "'Data' section of 'MS_METABOLITE_DATA' block do not match."
    ),

    # different "Metabolites" sections
    (
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test'), ('Value_1', 'Test')])],
        }},
        {'MS_METABOLITE_DATA': {
            'Units': 'test',
            'Data': [OrderedDict([('Metabolite', 'Test'), ('Subject_1', 1000)])],
            'Metabolites': [OrderedDict([('Metabolite', 'Test2'), ('Value_1', 'Test')])],
        }},
        "'Metabolites' section of 'MS_METABOLITE_DATA' block do not match."
    ),
])
def test_compare_data(mwtabfile_1, mwtabfile_2, error_msg):
    errors = mwFileStatusWebsite.compare.compare_data(mwtabfile_1, mwtabfile_2)
    assert not error_msg or any([error_msg in error.args[0] for error in errors])



def test_compare():
    tabfile1 = {'key1': 'asdf', 'SUBJECT_SAMPLE_FACTORS': [{'Sample ID': 'qwer'}]}
    tabfile2 = {'key2': 'asdf', 'SUBJECT_SAMPLE_FACTORS': [{'Sample ID': 'asdf'}]}
    errors = mwFileStatusWebsite.compare.compare(tabfile1, tabfile2)
    
    assert any(["mwTab files contain different blocks:" in error.args[0] for error in errors])
    assert any(["mwTab files contain different 'SUBJECT_SAMPLE_FACTORS' sections." in error.args[0] for error in errors])




