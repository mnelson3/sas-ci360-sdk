# SAS Customer Intelligence 360

## SAS 360 API CORE LIBRARY

### Overview

Foundational Python Library for building solutions against the SAS Customer Intelligence 360 REST API Collection.
<br><br>

### Table of Contents

This topic contains the following sections:

 - <a href="#prerequisites">Prerequisites</a>
 - <a href="#installation">Installation</a>
 - <a href="#getting-started">Getting Started</a>
 - <a href="#api-core-code">API Core Code</a>
 - <a href="#troubleshooting">Troubleshooting</a>
 - <a href="#contributing">Contributing</a>
 - <a href="#license">License</a>
 - <a href="#additional-resources">Additional Resources</a>
<br><br>

### Prerequisites

 * Required Python: >=3.6
<br><br>

### Installation

To install the SAS CI360 API Core Library from a package registry that hosts it:
 1. Open a terminal window (Unix/macOS) or command prompt (Windows)
 1. Copy and paste the following line at the cursor, substituting your own registry credentials<br>
    pip install sasci360apicore --extra-index-url https://\<username\>:\<token\>@\<your-package-registry\>/simple
 1. Press "Enter"<br>
    The SAS CI360 API Core Library should install

Alternatively, install directly from a clone of this repository:
 1. `git clone https://github.com/mnelson3/sas_ci360_api_core.git`
 1. `cd sas_ci360_api_core`
 1. `pip install .`
<br><br>

### Getting Started

While this library is available for review, please note that it is considered a work in process and NOT considered "released for production".
<br><br>

### API Core Code

 1. Communication - Contains operations to send emails
 1. Connection - Contains operations to connect to REST APIs
 1. Data - Contains operations to form and manipulate data structures
 1. Encryption - Contains operations to encrypt data
 1. Listener - Contains operations to watch for and relay files
 1. Logger - Contains operations to configure application logging
 1. Reporter - Contains operations to persist JSON data to disk
 1. Scheduler - Contains operations to run jobs on a recurring schedule
<br><br>

### Troubleshooting

For issues specific to sasci360apicore try updating the library.

To update sasci360apicore:
 1. Open a terminal window (Unix/macOS) or command prompt (Windows)
 1. Copy and paste the following line at the cursor<br>
    pip uninstall sasci360apicore
 1. Press "Enter"<br>
    The SAS CI360 API Core Library should uninstall
 1. Copy and paste the following line at the cursor, substituting your own registry credentials<br>
    pip install sasci360apicore --extra-index-url https://\<username\>:\<token\>@\<your-package-registry\>/simple
 1. Press "Enter"<br>
    The SAS CI360 API Core Library should install<br><br>

### Contributing

We welcome your contributions! Please read [CONTRIBUTING](CONTRIBUTING) for details on how to submit contributions to this project.
<br><br>

### License

This project is licensed under the [Apache 2.0 License](LICENSE).
<br><br>

### Additional Resources

For more information, see [REST APIs](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/ch-rest-apis.htm).
<br><br>
