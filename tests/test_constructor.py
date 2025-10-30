# -*- coding: utf-8 -*-
"""
Test the few lines in constructor that aren't tested by simply running the cli tests.
"""

import mwFileStatusWebsite



def test_filter_analyses_by_status():
    validation_dict = {'ST000001': {'params':{}, 'analyses':{'AN000001': {'status': {'json': 'Passing', 'txt': 'Passing'}}}},
                       'ST000002': {'params':{}, 'analyses':{'AN000002': {'status': {'json': 'Warnings', 'txt': 'Passing'}}}}}
    status_dict = mwFileStatusWebsite.constructor.filter_analyses_by_status(validation_dict, 'Passing')
    assert status_dict == validation_dict
    
    status_dict = mwFileStatusWebsite.constructor.filter_analyses_by_status(validation_dict, 'Passing', True)
    assert status_dict == {'ST000001': {'params':{}, 'analyses':{'AN000001': {'status': {'json': 'Passing', 'txt': 'Passing'}}}}}


def test_filter_analyses_by_issues():
    validation_dict = {'ST000001': {'params':{}, 'analyses':{'AN000001': {'issues': {'json': {'value': True}, 'txt': {'value': True}}}}},
                       'ST000002': {'params':{}, 'analyses':{'AN000002': {'issues': {'json': {'value': False}, 'txt': {'value': True}}}}}}
    status_dict = mwFileStatusWebsite.constructor.filter_analyses_by_issues(validation_dict, 'value')
    assert status_dict == validation_dict
    
    status_dict = mwFileStatusWebsite.constructor.filter_analyses_by_issues(validation_dict, 'value', True)
    assert status_dict == {'ST000001': {'params':{}, 'analyses':{'AN000001': {'issues': {'json': {'value': True}, 'txt': {'value': True}}}}}}
