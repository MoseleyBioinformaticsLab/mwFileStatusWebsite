# -*- coding: utf-8 -*-
import pytest
from mwFileStatusWebsite import cli
import mwtab
import pathlib
import shutil
import time
import json
import subprocess


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

def read_test_data(an_id, file_format):
    path = f'tests/test_files/https%3A%2F%2Fwww_metabolomicsworkbench_org%2Frest%2Fstudy%2Fanalysis_id%2F{an_id}%2Fmwtab%2F{file_format}.{file_format}'
    tabfile = mwtab.mwtab.MWTabFile(str(path), duplicate_keys=True)
    with open(path, encoding="utf-8") as f:
        tabfile.read(f)
    yield tabfile



def test_cli_validate(study_analysis_dict, mocker, capsys, disable_sleep, init_tmp_dir):
    """Have to call cli function instead of calling through the system, because we need to mock so much stuff."""
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict])
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [read_test_data('AN000001', 'txt'),
                                                                                  read_test_data('AN000001', 'json'),
                                                                                  read_test_data('AN000023', 'txt'),
                                                                                  read_test_data('AN000023', 'json'),
                                                                                  read_test_data('AN000024', 'txt'),
                                                                                  read_test_data('AN000024', 'json')])
    
    cli.cli({'--logs-path': TMP_PATH, '--output-path': TMP_PATH, '--verbose': True, 'validate':True})
    captured = capsys.readouterr()
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


def test_cli_generate(study_analysis_dict, mocker, disable_sleep, init_tmp_dir):
    mocker.patch('mwFileStatusWebsite.validator.mwtab.mwrest._pull_study_analysis', side_effect = [study_analysis_dict])
    mocker.patch('mwFileStatusWebsite.validator.mwtab.read_files', side_effect = [read_test_data('AN000001', 'txt'),
                                                                                  read_test_data('AN000001', 'json'),
                                                                                  read_test_data('AN000023', 'txt'),
                                                                                  read_test_data('AN000023', 'json'),
                                                                                  read_test_data('AN000024', 'txt'),
                                                                                  read_test_data('AN000024', 'json')])
    
    cli.cli({'--logs-path': TMP_PATH, '--output-path': TMP_PATH, '--verbose': True, 'validate':True})
    
    command = f"mwFileStatusWebsite generate --html-path={TMP_PATH} --validation-json={TMP_PATH + 'tmp.json'}"
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    assert subp.returncode == 0
    assert pathlib.Path(TMP_PATH + 'consistency.html').exists()
    assert pathlib.Path(TMP_PATH + 'format.html').exists()
    assert pathlib.Path(TMP_PATH + 'index.html').exists()
    assert pathlib.Path(TMP_PATH + 'missing.html').exists()
    assert pathlib.Path(TMP_PATH + 'parsing_error.html').exists()
    assert pathlib.Path(TMP_PATH + 'passing.html').exists()
    assert pathlib.Path(TMP_PATH + 'validation_error.html').exists()
    assert pathlib.Path(TMP_PATH + 'value.html').exists()
    assert pathlib.Path(TMP_PATH + 'warnings_only.html').exists()






