# XNAT Wrapper Documentation

## Introduction

This is designed to be a wrapper that streamlines the functionality of
[pyxnat][], allowing the user to easily create, edit, and run analysis
functions on XNAT projects, sessions, and scans.

## TODO

-   Add function to create new project
-   Add function to pull headers from DICOM metadata
-   Add function to convert MRIQC data from CSV/table to "box and
    whisker" plots

## Installation

As the package has not been published on PyPi yet, it CANNOT be install
using pip.

The only Python package that must be installed prior to running the
example(s) is [pyxnat][], which can be installed by running
`python3 -m pip install -r requirements.txt` or [directly from PyPi][]
using `python3 -m pip install pyxnat`.

Once the required packages are installed, the wrapper must be imported
to your script/project by importing the wrapper's `Connector` class. For
more detailed instructions on usage and classes, see [Examples and
APIs][]).

## Usage

The `xnat_wrapper` utility consists of three classes:

-   Connector (`xnat_wrapper.Connector`)

    > -   UIDImporter (`Connector.importer`)
    > -   CommandUtility (`Connector.commands`)

To start an XNAT connection, initialize the connector class using either
of these options (optionally including a project name): By supplying the
server, username, and password:

``` python
xnat = Connector(server='your.xnat.instance.ip.address',
                user='username',
                password='password',
                project='project_name')
```

or by supplying a configuration file containing all three (in JSON
format):

``` python
xnat = Connector(config='xnat_login.cfg', 
                project='project_name')
```

Access the importer utility to set a list of UIDs, find them, and import
them into your project:

``` python
xnat.importer.set_uids(uid_list)
xnat.importer.find_studies()
import_success = xnat.importer.import_studies()
```

After successfully importing your studies, you can monitor the import
queue using:

``` python
if import_success:
    xnat.importer.monitor_import_queue()
```

Once the studies have been imported and downloaded, they can be accessed
by using:

``` python
project_studies = xnat.importer.get_studies()
```

Once that process is complete, you will need to close the XNAT session
before exiting the program using:

``` python
xnat.close_session()
```

## Examples and APIs

For a more in-depth example of functionality, see:

<div class="toctree" maxdepth="2" caption="Examples">

examples

</div>

<div class="toctree" maxdepth="2" caption="APIs">

pages/connector pages/uid\_importer pages/command\_utility

</div>

  [pyxnat]: https://pyxnat.github.io/pyxnat/
  [directly from PyPi]: https://pypi.org/project/pyxnat/
  [Examples and APIs]: #examples-and-apis
