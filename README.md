# XNAT Wrapper Documentation

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/jwood1290/XNAT_Wrapper/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://xnat-wrapper.readthedocs.io/en/latest/)

## Introduction

`xnat_wrapper` is designed to be a wrapper that streamlines the functionality of [pyxnat](https://pyxnat.github.io/pyxnat), allowing the user to easily create, edit, and run analysis functions on XNAT projects, sessions, and scans.

## Installation

As the package has not been published on PyPi yet, it CANNOT be install using pip.

The only Python package that must be installed prior to running the example(s) is [pyxnat](https://pyxnat.github.io/pyxnat), which can be installed by running `python3 -m pip install -r requirements.txt` or [directly from PyPi](https://pypi.org/project/pyxnat) using `python3 -m pip install pyxnat`.

Once the required packages are installed, the wrapper must be imported to your script/project by importing the wrapper's `Connector` class. For more detailed instructions on usage and classes, see the [documentation](https://xnat-wrapper.readthedocs.io/en/latest/examples.html).

## Usage

`xnat_wrapper` consists of three classes:

- Connector (`xnat_wrapper.Connector`)
  - UIDImporter (`Connector.importer`)
  - CommandUtility (`Connector.commands`)

To start an XNAT connection, initialize the connector class using either of these options (optionally including a project name): By supplying the server, username, and password:

``` python
from xnat_wrapper import Connector

xnat = Connector(server='your.xnat.instance.ip.address',
                user='username',
                password='password',
                project='project_name')
```

or by supplying a configuration file containing all three (in JSON format):

``` python
xnat = Connector(config='xnat_login.cfg', 
                project='project_name')
```

Access the importer utility to set a list of UIDs, find them, and import them into your project:

``` python
xnat.importer.set_uids(uid_list)
xnat.importer.find_studies()
import_success = xnat.importer.import_studies()
```

After successfully importing your studies, you can monitor the import queue using:

``` python
if import_success:
    xnat.importer.monitor_import_queue()
```

Once the studies have been imported and downloaded, they can be accessed by using:

``` python
project_studies = xnat.importer.get_studies()
```

Once that process is complete, you will need to close the XNAT session before exiting the program using:

``` python
xnat.close_session()
```

## TODO

- Add function to create new project
- Add function to pull headers from DICOM metadata
- Add function to convert MRIQC data from CSV/table to "box and whisker" plots
