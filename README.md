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

The `mwFilesStatus` website can be run locally but is intended to be setup on a Virtual Machine for automated updating.


### Basic Installation

Clone the repository
```bash
git clone git@github.com:MoseleyBioinformaticsLab/mwFileStatusWebsite.git
cd mwFileStatusWebsite
```

Create a virtual environment and install the `mwFileStatusWebsite` package locally through `pip`.
```python
python3 -m virtualenv venv
source venv/bin/activate
python3 -m pip install -e ../mwFileStatusWebsite
```


### Installation for Virtual Machine Usage

Coming soon


## Usage

### Commandline Usage

```bash
mwFilesStatusWebsite validate
mwFilesStatusWebsite generate
```

### Python3 Usage

```bash
python3 -m mwFilesStatusWebsite validate
python3 -m mwFilesStatusWebsite generate
```

## License

This package is distributed under the [BSD](https://choosealicense.com/licenses/bsd-3-clause-clear/) `license`.
