#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The mwFileStatusWebsite command-line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    mwFileStatusWebsite -h | --help
    mwFileStatusWebsite --version
    mwFileStatusWebsite validate [--to-path=<path>]
    mwFileStatusWebsite generate

Options:
    -h, --help                      Show this screen.
    --version                       Show version.
    --verbose                       Enable verbose processing.
    --to-path=<path>                Path to directory for retrieved analyses to be saved in.
"""
from . import validator, constructor


def cli(cmdargs):

    if cmdargs['validate']:
        validator.validate_mwtab_rest(save_path=cmdargs['--to-path'])

    elif cmdargs['generate']:
        # create the main webpage (index.html)
        validation_dict = constructor.load_json('tmp.json')
        config_dict = constructor.load_json('docs/config.json')
        constructor.create_html(validation_dict, config_dict, 'index.html')

        # create the passing.html page
        # contains only analyses which one or both formats (mwTab and JSON) are passing
        passing = constructor.create_error_dicts(validation_dict, 'Passing', True)
        constructor.create_html(passing, config_dict, 'passing.html')

        # create the validation_error.html page
        # contains analyses which both formats (mwTab and JSON) have validation errors.
        validation = constructor.create_error_dicts(validation_dict, 'Validation Error')
        constructor.create_html(validation, config_dict, 'validation_error.html')

        # create the parsing_error.html page
        # contains analyses which both formats (mwTab and JSON) have parsing errors.
        parsing = constructor.create_error_dicts(validation_dict, 'Parsing Error')
        constructor.create_html(parsing, config_dict, 'parsing_error.html')

        # create the missing.html page
        # contains analyses which both formats (mwTab and JSON) are missing.
        missing = constructor.create_error_dicts(validation_dict, 'Missing/Blank')
        constructor.create_html(missing, config_dict, 'missing.html')
