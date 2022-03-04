# Metabolomics Workbench File Status Website

This repository holds the scripts required for creating 
and updating the Metabolomics Workbench File Status 
website along with the validation longs for each 
available analysis in both `JSON` and `mwTab` file 
formats.


## Usage

The Metabolomics Workbench File Status website can be 
accessed through it's GitHub Pages hosted webpage at: 

https://moseleybioinformaticslab.github.io/mwFileStatusWebsite/

Individual validation files can be accessed in the 
[docs/validation_logs/](https://github.com/moseleybioinformaticslab/mwFileStatusWebsite/tree/master/docs/validation_logs) 
directory in this repository.

## Installation

### Setup Git ssh

### Setup Virtualenv
```python3 -m setup.py```

### Running update scripts
```
python3 validator.py
python3 generate_html.py
```

## License

This package is distributed under the BSD_ `license`.

.. _BSD: https://choosealicense.com/licenses/bsd-3-clause-clear/
