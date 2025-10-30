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
import pathlib
import shutil
import time
import json


TMP_PATH = "tests/tmp/"

def create_tmp_dir():
    path = pathlib.Path(TMP_PATH)
    path.mkdir(parents=True)

def delete_tmp_dir():
    path = pathlib.Path(TMP_PATH)
    if path.exists():
        shutil.rmtree(path)
        time_to_wait=10
        time_counter = 0
        while path.exists():
            time.sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:
                raise FileExistsError(path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

@pytest.fixture()
def init_tmp_dir():
    delete_tmp_dir()
    create_tmp_dir()
    yield
    delete_tmp_dir()



@pytest.fixture()
def disable_sleep(monkeypatch):
    def no_sleep(arg):
        pass
    monkeypatch.setattr('mwFileStatusWebsite.validator.sleep', no_sleep)

@pytest.fixture(scope='module')
def study_analysis_dict():
    with open('tests/test_files/study_analysis_dict.json', 'r') as jsonFile:
        study_analysis_dict = json.load(jsonFile)
    yield study_analysis_dict

@pytest.fixture(scope='module')
def study_analysis_dict2():
    with open('tests/test_files/study_analysis_dict2.json', 'r') as jsonFile:
        study_analysis_dict = json.load(jsonFile)
    yield study_analysis_dict

def read_test_data(an_id, file_format):
    path = f'tests/test_files/https%3A%2F%2Fwww_metabolomicsworkbench_org%2Frest%2Fstudy%2Fanalysis_id%2F{an_id}%2Fmwtab%2F{file_format}.{file_format}'
    tabfile = mwtab.mwtab.MWTabFile(str(path), duplicate_keys=True)
    with open(path, encoding="utf-8") as f:
        tabfile.read(f)
    yield tabfile



def test_validate_mwtab_rest_mocked(study_analysis_dict, mocker, capsys, disable_sleep, init_tmp_dir):
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict])
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [read_test_data('AN000001', 'txt'),
                                                                                  read_test_data('AN000001', 'json'),
                                                                                  read_test_data('AN000023', 'txt'),
                                                                                  read_test_data('AN000023', 'json'),
                                                                                  read_test_data('AN000024', 'txt'),
                                                                                  read_test_data('AN000024', 'json')])
    
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_rest(logs_path = TMP_PATH, output_file = TMP_PATH + 'tmp.json', verbose = True)
    captured = capsys.readouterr()
    assert len(validation_dict) == 2
    assert 'Validating study: ST000001' in captured.out
    assert 'Validating study: ST000009' in captured.out
    assert pathlib.Path(TMP_PATH + 'AN000001_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'tmp.json').exists()

def test_validate_mwtab_rest_mocked2(study_analysis_dict2, mocker, capsys, disable_sleep, init_tmp_dir):
    """Hitting some more lines not covered by the previous test."""
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict2])
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [read_test_data('AN002319', 'txt'),
                                                                                  read_test_data('AN002319', 'json'),
                                                                                  read_test_data('AN003788', 'txt'),
                                                                                  read_test_data('AN003788', 'json')])
    
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_rest(logs_path = TMP_PATH, 
                                                                        output_file = TMP_PATH + 'tmp.json', 
                                                                        save_path = TMP_PATH,
                                                                        verbose = True)
    captured = capsys.readouterr()
    assert len(validation_dict) == 2
    assert 'Validating study: ST001390' in captured.out
    assert 'Validating study: ST002321' in captured.out
    assert pathlib.Path(TMP_PATH + 'AN002319_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN002319_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN002319_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN003788_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN003788_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN003788_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'tmp.json').exists()
    assert validation_dict['ST002321']["analyses"]['AN003788']["status"]['comparison'] == "Inconsistent"
    assert pathlib.Path(TMP_PATH + 'AN002319.txt').exists()
    assert pathlib.Path(TMP_PATH + 'AN002319.json').exists()
    assert pathlib.Path(TMP_PATH + 'AN003788.txt').exists()
    assert pathlib.Path(TMP_PATH + 'AN003788.json').exists()


def test_server_recovery(study_analysis_dict, mocker, capsys, disable_sleep, init_tmp_dir):
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict])
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [Exception(),
                                                                                  read_test_data('AN000001', 'txt'),
                                                                                  read_test_data('AN000001', 'json'),
                                                                                  read_test_data('AN000023', 'txt'),
                                                                                  read_test_data('AN000023', 'json'),
                                                                                  read_test_data('AN000024', 'txt'),
                                                                                  read_test_data('AN000024', 'json')])
    
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_rest(logs_path = TMP_PATH, output_file = TMP_PATH + 'tmp.json', verbose = True)
    captured = capsys.readouterr()
    assert len(validation_dict) == 2
    assert 'Validating study: ST000001' in captured.out
    assert 'Validating study: ST000009' in captured.out
    assert pathlib.Path(TMP_PATH + 'AN000001_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'tmp.json').exists()


def test_validate_mwtab_rest_exceptions(study_analysis_dict, mocker, capsys, disable_sleep, init_tmp_dir):
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict])
    # Errors are retried 3 times, so they are in there a total of 4 times to get things right.
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [ValueError("Blank input string retrieved from source."),
                                                                                  ValueError("Blank input string retrieved from source."),
                                                                                  ValueError("Blank input string retrieved from source."),
                                                                                  ValueError("Blank input string retrieved from source."),
                                                                                  read_test_data('AN000001', 'json'),
                                                                                  read_test_data('AN000023', 'txt'),
                                                                                  ValueError(""),
                                                                                  ValueError(""),
                                                                                  ValueError(""),
                                                                                  ValueError(""),
                                                                                  read_test_data('AN000024', 'txt'),
                                                                                  read_test_data('AN000024', 'json')])
    
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_rest(logs_path = TMP_PATH, output_file = TMP_PATH + 'tmp.json', verbose = True)
    captured = capsys.readouterr()
    assert len(validation_dict) == 2
    assert 'Validating study: ST000001' in captured.out
    assert 'Validating study: ST000009' in captured.out
    assert not pathlib.Path(TMP_PATH + 'AN000001_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_txt.log').exists()
    assert not pathlib.Path(TMP_PATH + 'AN000023_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000023_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000024_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'tmp.json').exists()
    assert validation_dict['ST000001']["analyses"]['AN000001']["status"]['txt'] == "Missing/Blank"
    assert validation_dict['ST000009']["analyses"]['AN000023']["status"]['json'] == "Parsing Error"


def test_validate_mwtab_rest(capsys, init_tmp_dir):
    """No mocking. Test that downloading and validating from the Workbench works."""
    validation_dict = mwFileStatusWebsite.validator.validate_mwtab_rest(input_dict={'ST000001': ['AN000001']}, 
                                                                        logs_path = TMP_PATH, 
                                                                        output_file = TMP_PATH + 'tmp.json', 
                                                                        verbose = True)

    captured = capsys.readouterr()
    assert len(validation_dict) == 1
    assert 'Validating study: ST000001' in captured.out
    assert pathlib.Path(TMP_PATH + 'AN000001_comparison.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_txt.log').exists()
    assert pathlib.Path(TMP_PATH + 'AN000001_json.log').exists()
    assert pathlib.Path(TMP_PATH + 'tmp.json').exists()


def test_retrieve_mwtab_files_exception(capsys, mocker):
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [Exception()])
    with pytest.raises(SystemExit):
        mwFileStatusWebsite.validator.retrieve_mwtab_files()

    captured = capsys.readouterr()
    assert "Unable to access https://www.metabolomicsworkbench.org/" in captured.out


