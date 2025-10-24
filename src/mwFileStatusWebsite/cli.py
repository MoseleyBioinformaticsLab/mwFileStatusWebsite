#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The mwFileStatusWebsite command-line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    mwFileStatusWebsite -h | --help
    mwFileStatusWebsite --version
    mwFileStatusWebsite validate [--to-path=<path>] [--verbose]
    mwFileStatusWebsite generate

Options:
    -h, --help                      Show this screen.
    --version                       Show version.
    --verbose                       Enable verbose processing.
    --to-path=<path>                Directory to save the downloaded mwTab analysis files to.
"""
from . import validator, constructor

def cli(cmdargs):

    if cmdargs['validate']:
        validator.validate_mwtab_rest(save_path=cmdargs['--to-path'], verbose = cmdargs.get('--verbose', False))

    elif cmdargs['generate']:
        # create the main webpage (index.html)
        validation_dict = constructor.load_json('tmp.json')
        config_dict = constructor.load_json('docs/config.json')
        constructor.create_html(validation_dict, config_dict, 'index.html')

        # create the passing.html page
        # contains only analyses which one or both formats (mwTab and JSON) are passing
        passing = constructor.filter_analyses_by_status(validation_dict, 'Passing', True)
        constructor.create_html(passing, config_dict, 'passing.html')
        
        # create the warnings_only.html page
        # contains analyses which both formats (mwTab and JSON) have only warnings.
        warnings = constructor.filter_analyses_by_status(validation_dict, 'Warnings Only')
        constructor.create_html(warnings, config_dict, 'warnings_only.html')

        # create the validation_error.html page
        # contains analyses which both formats (mwTab and JSON) have validation errors.
        validation = constructor.filter_analyses_by_status(validation_dict, 'Validation Error')
        constructor.create_html(validation, config_dict, 'validation_error.html')

        # create the parsing_error.html page
        # contains analyses which both formats (mwTab and JSON) have parsing errors.
        parsing = constructor.filter_analyses_by_status(validation_dict, 'Parsing Error')
        constructor.create_html(parsing, config_dict, 'parsing_error.html')

        # create the missing.html page
        # contains analyses which both formats (mwTab and JSON) are missing.
        missing = constructor.filter_analyses_by_status(validation_dict, 'Missing/Blank')
        constructor.create_html(missing, config_dict, 'missing.html')
        
        
        # create the value.html page
        # contains analyses where one or both formats (mwTab and JSON) have value errors.
        passing = constructor.filter_analyses_by_issues(validation_dict, 'value')
        constructor.create_html(passing, config_dict, 'value.html')

        # create the consistency.html page
        # contains analyses where one or both formats (mwTab and JSON) have consistency errors.
        consistency = constructor.filter_analyses_by_issues(validation_dict, 'consistency')
        constructor.create_html(consistency, config_dict, 'consistency.html')

        # create the format.html page
        # contains analyses where one or both formats (mwTab and JSON) have format errors.
        format_dict = constructor.filter_analyses_by_issues(validation_dict, 'format')
        constructor.create_html(format_dict, config_dict, 'format.html')

        # create the warning.html page
        # contains analyses where one or both formats (mwTab and JSON) have warnings.
        # warning = constructor.filter_analyses_by_issues(validation_dict, 'warnings')
        # constructor.create_html(warning, config_dict, 'warning.html')
