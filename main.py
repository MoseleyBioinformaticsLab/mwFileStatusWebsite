import mwtab
from datetime import datetime
import re
import mwFileStatusWebsite
import json


VERBOSE = True


if __name__ == '__main__':
    # study_analysis_dict = validator.retrieve_mwtab_files(True)
    # with open('files.json', 'w') as fh:
    #     fh.write(json.dumps(study_analysis_dict))

    try:
        mwtabfile = next(mwtab.read_files(mwFileStatusWebsite.MW_REST_URL.format('AN000012', 'txt')))
        validated_mwtabfile, validation_log = mwtab.validate_file(mwtabfile, metabolites=False)
    except Exception as e:
        print(e)
