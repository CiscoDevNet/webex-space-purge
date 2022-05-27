# webex-space-purge

## Overview

Purge all users from a space who have not posted a message since a specified cut-off date.

This can help pare down space membership when approaching the 5K limit.

Components used:

* [WebexTeamsSDK Python library](https://github.com/CiscoDevNet/webexteamssdk) for Teams data retrieval

* [SQLite](https://www.sqlite.org/index.html) for data storage/analysis

* [SQLite Studio](https://sqlitestudio.pl/)  GUI helpful for browsing schemas/data and testing SQL

Tested using:

* OS: Ubuntu Linux 22.04
* Python: 3.10.4

[Webex for Developers Site](https://developer.webex.com/)

## Getting started

* Install Python 3.10+

    On Windows, choose the option to add to PATH environment variable

* The project was built/tested using [Visual Studio Code](https://code.visualstudio.com/)

    On first launch of VS Code, [install the Python plugin](https://code.visualstudio.com/docs/languages/python)

* Clone this repo to a directory on your PC:

    ```bash
    git clone https://github.com/CiscoDevNet/webex-space-purge.git
    cd webex-space-purge
    ```

* (Optional) Create and activate a Python virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

* Dependency Installation:

    ```bash
    pip install -r requirements.txt
    ```
  
* Open the project in VS Code:

    ```bash
    code .
    ```

* Visit [https://developer.webex.com/docs/getting-started#accounts-and-authentication), login, and copy your personal access token

* In Visual Studio Code:

    * Rename `.env.example` to `.env` and edit to configure

    * Press **F5** to run the application

      or

      ```
      python webex_space_purge.py

> **Note:** at the moment, line 105 in webex_space_purge.py is commented out:

  ```python
  api.memberships.delete(row['id'])
  ```

  Uncomment this line to arm the code for real purging!

* After messages/memberships are retrieved and the list of users to be purged is queried, the Webex user email will be written to `purge_list.txt`.

  You may want to examine this file as a sanity check.

* Finally: you will be asked to type in `CONFIRM` before any users are actually purged.

> **Note:** If something goes wrong, it should theoretically be possible to recreate purged memberships based on the purge_list.txt file.
