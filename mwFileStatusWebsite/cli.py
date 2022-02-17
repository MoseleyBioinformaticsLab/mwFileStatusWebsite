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
from . import validator, generate_html


def cli(cmdargs):

    if cmdargs['validate']:
        validator.validate_mwtab_files(save_path=cmdargs['--to-path'])

    elif cmdargs['generate']:
        # create the main webpage (index.html)
        validation_dict = generate_html.load_json('tmp.json')
        config_dict = generate_html.load_json('docs/config.json')
        generate_html.create_html(validation_dict, config_dict, 'index.html')

        # create the passing.html page
        # contains only analyses which both formats (mwTab and JSON) are passing
        passing = generate_html.create_error_dicts(validation_dict, 'Passing', True)
        generate_html.create_html(passing, config_dict, 'passing.html')

        # create the validation_error.html page
        # contains analyses which one or both formats (mwTab and JSON) have validation errors.
        validation = generate_html.create_error_dicts(validation_dict, 'Validation Error')
        generate_html.create_html(validation, config_dict, 'validation_error.html')

        # create the parsing_error.html page
        # contains analyses which one or both formats (mwTab and JSON) have parsing errors.
        parsing = generate_html.create_error_dicts(validation_dict, 'Parsing Error')
        generate_html.create_html(parsing, config_dict, 'parsing_error.html')

        # create the missing.html page
        # contains analyses which one or both formats (mwTab and JSON) are missing.
        missing = generate_html.create_error_dicts(validation_dict, 'Missing/Blank')
        generate_html.create_html(missing, config_dict, 'missing.html')
