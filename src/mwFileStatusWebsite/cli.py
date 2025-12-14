#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The mwFileStatusWebsite command-line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    mwFileStatusWebsite -h | --help
    mwFileStatusWebsite --version
    mwFileStatusWebsite validate [--to-path=<path>] [--logs-path=<path>] [--output-path=<path>] [--verbose]
    mwFileStatusWebsite generate [--html-path=<path>] [--owner=<owner>] [--repo-name=<name>] [--validation-json=<path>]

Options:
    -h, --help                      Show this screen.
    --version                       Show version.
    --verbose                       Enable verbose processing.
    --to-path=<path>                Directory to save the downloaded mwTab analysis files to. Files are not saved unless this is given.
    --logs-path=<path>              Directory to save the validation log files to [default: validation_logs].
    --output-path=<path>            Directory to save the validation summary JSON file to. Defaults to the CWD.
    --html-path=<path>              Directory to save html files to. Defaults to the CWD.
    --owner=<owner>                 The GitHub account name that owns the repo where the html files will be committed to [default: MoseleyBioinformaticsLab].
    --repo-name=<name>              The name of the repo where the html files will be committed to [default: mwFileStatusWebsite].
    --validation-json=<path>        The path to the validation JSON summary output by the validate command [default: tmp.json].
"""
from . import validator, constructor
import os

def cli(cmdargs):

    if cmdargs['validate']:
        validator.validate_mwtab_rest(logs_path = cmdargs['--logs-path'], 
                                      output_file = os.path.join(cmdargs['--output-path'] if cmdargs['--output-path'] else '', 'tmp.json'),
                                      save_path = cmdargs['--to-path'], verbose = cmdargs.get('--verbose', False))

    elif cmdargs['generate']:
        html_path = cmdargs['--html-path'] if cmdargs['--html-path'] else ''
        validation_path = cmdargs['--validation-json']
        owner = cmdargs['--owner']
        repo = cmdargs['--repo-name']
        
        # create the main webpage (index.html)
        validation_dict = constructor.load_json(validation_path)
        
        constructor.create_html(validation_dict, owner, repo, os.path.join(html_path, 'index.html'))

        # create the passing.html page
        # contains only analyses which one or both formats (mwTab and JSON) are passing
        passing = constructor.filter_analyses_by_status(validation_dict, 'Passing', True)
        constructor.create_html(passing, owner, repo, os.path.join(html_path, 'passing.html'))
        
        # create the warnings_only.html page
        # contains analyses which both formats (mwTab and JSON) have only warnings.
        warnings = constructor.filter_analyses_by_status(validation_dict, 'Warnings Only')
        constructor.create_html(warnings, owner, repo, os.path.join(html_path, 'warnings_only.html'))

        # create the validation_error.html page
        # contains analyses which both formats (mwTab and JSON) have validation errors.
        validation = constructor.filter_analyses_by_status(validation_dict, 'Validation Error')
        constructor.create_html(validation, owner, repo, os.path.join(html_path, 'validation_error.html'))

        # create the parsing_error.html page
        # contains analyses which both formats (mwTab and JSON) have parsing errors.
        parsing = constructor.filter_analyses_by_status(validation_dict, 'Parsing Error')
        constructor.create_html(parsing, owner, repo, os.path.join(html_path, 'parsing_error.html'))

        # create the missing.html page
        # contains analyses which both formats (mwTab and JSON) are missing.
        missing = constructor.filter_analyses_by_status(validation_dict, 'Missing/Blank')
        constructor.create_html(missing, owner, repo, os.path.join(html_path, 'missing.html'))
        
        
        # create the value.html page
        # contains analyses where one or both formats (mwTab and JSON) have value errors.
        passing = constructor.filter_analyses_by_issues(validation_dict, 'value')
        constructor.create_html(passing, owner, repo, os.path.join(html_path, 'value.html'))

        # create the consistency.html page
        # contains analyses where one or both formats (mwTab and JSON) have consistency errors.
        consistency = constructor.filter_analyses_by_issues(validation_dict, 'consistency')
        constructor.create_html(consistency, owner, repo, os.path.join(html_path, 'consistency.html'))

        # create the format.html page
        # contains analyses where one or both formats (mwTab and JSON) have format errors.
        format_dict = constructor.filter_analyses_by_issues(validation_dict, 'format')
        constructor.create_html(format_dict, owner, repo, os.path.join(html_path, 'format.html'))

        # create the warning.html page
        # contains analyses where one or both formats (mwTab and JSON) have warnings.
        # warning = constructor.filter_analyses_by_issues(validation_dict, 'warnings')
        # constructor.create_html(warning, owner, repo, os.path.join(html_path, 'warning.html'))
