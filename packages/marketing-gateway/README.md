# SAS Customer Intelligence 360

## SAS 360 API MARKETING GATEWAY LIBRARY

> **Status: canonical.** This is the actively maintained client for the Marketing Gateway API (Discover data downloads). No newer `sol-*` equivalent exists yet.

### Overview

The Marketing Gateway API provides access to a variety of features in SAS Customer Intelligence 360. You can use this API to perform tasks like downloading data records and injecting external events.

For detailed information on REST API:<br>
https://support.sas.com/documentation/onlinedoc/ci/ci360-apis/marketingGateway/v2/redoc.html
<br><br>

### Table of Contents

This topic contains the following sections:

 - <a href="#prerequisites">Prerequisites</a>
 - <a href="#installation">Installation</a>
 - <a href="#getting-started">Getting Started</a>
 - <a href="#api-marketing-gateway-code">API Marketing Gateway Code</a>
 - <a href="#troubleshooting">Troubleshooting</a>
 - <a href="#contributing">Contributing</a>
 - <a href="#license">License</a>
 - <a href="#additional-resources">Additional Resources</a>
<br><br>

### Prerequisites

 * Required Python: >=3.6
 * Customer Intelligence 360 Tenant with Administrative Rights<
 * SAS CI360 API Core Library:<br>
   https://gitlab.sas.com/psd-ci-enablement/sas_ci360_api_core
<br><br>

### Installation

To install the SAS CI360 API Marketing Gateway Library:
 1. Open a terminal window (Unix/macOS) or command prompt (Windows)
 1. Copy and paste the following line at the cursor<br>
    pip install sasci360apimarketinggateway --extra-index-url https://<username>:<deploy-token>@gitlab.sas.com/api/v4/projects/49171/packages/pypi/simple
 1. Press "Enter"<br>
    The SAS CI360 API Marketing Gateway Library should install

Replace `<username>` and `<deploy-token>` with the credentials for the GitLab package registry (request access from the psd-ci-enablement team). Do not commit real credentials into this URL.
<br><br>

### Getting Started

While this library is available for review, please note that it is considered a work in process and NOT considered "released for production".
<br><br>

### API Marketing Gateway Code

 1. Agents - Contains the operations for downloading on-premises agents. To download the on-premises SDK, use the /agent endpoint to download the general agent (which includes the SDK). Note: This call does not require authentication. The response is a direct download of the .zip file. Refer to the instructions for your REST API client if you have issues processing the response.
 1. Configuration - Contains the operations to see your API configuration.
 1. Data Download - Returns the links to download the Discover Base Tables (DBTs) and Analytical Base Tables (ABTs). These tables are updated about every four hours. Only completed sessions are available for download.
 1. Events - Contains operations to upload bulk events or inject single events. Note: Injected events must have corresponding external events that are already defined in SAS Customer Intelligence 360. For more information, see Working with External Events.
 1. Root - Contains the operations for this root resource.
<br><br>

### Troubleshooting

For issues specific to sasci360apicore or sasci360apimarketinggateway try updating the libraries.

To update sasci360apicore:
 1. Open a terminal window (Unix/macOS) or command prompt (Windows)
 1. Copy and paste the following line at the cursor<br>
    pip uninstall sasci360apicore
 1. Press "Enter"<br>
    The SAS CI360 API Core Library should uninstall
 1. Copy and paste the following line at the cursor<br>
    pip install sasci360apicore --extra-index-url https://<username>:<deploy-token>@gitlab.sas.com/api/v4/projects/35734/packages/pypi/simple
 1. Press "Enter"<br>
    The SAS CI360 API Core Library should install

To update sasci360apimarketinggateway:
 1. Open a terminal window (Unix/macOS) or command prompt (Windows)
 1. Copy and paste the following line at the cursor<br>
    pip uninstall sasci360apimarketinggateway
 1. Press "Enter"<br>
    The SAS CI360 API Marketing Gateway Library should uninstall
 1. Copy and paste the following line at the cursor<br>
    pip install sasci360apimarketinggateway --extra-index-url https://<username>:<deploy-token>@gitlab.sas.com/api/v4/projects/49171/packages/pypi/simple
 1. Press "Enter"<br>
    The SAS CI360 API Marketing Gateway Library should install
<br><br>

### Contributing

We welcome your contributions! Please read [CONTRIBUTING](CONTRIBUTING.md) for details on how to submit contributions to this project.
<br><br>

### License

This project is licensed under the [Nelson Grey LLC Community License 1.0](LICENSE).

- **Free for individuals, education, and research**: use, modify, and distribute this software for non-commercial purposes
- **Commercial evaluation**: evaluate the software for a possible commercial use, free of charge
- **Commercial production use**: requires a commercial license from Nelson Grey LLC
- **Automatic conversion**: on December 13, 2029, this automatically converts to the Apache License 2.0

For commercial licensing inquiries, contact support@nelsongrey.com.

### Additional Resources

For more information, see [REST APIs](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/ch-rest-apis.htm).
<br><br>
