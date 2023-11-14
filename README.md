# Create and send report

## File with report

Each line has time, name, type and project they are divided by space-dash-space:

```
[hour] [minute] - [name of task] - [name of type] - [name of project]
```

Example:

```
09 00 - 0123456: Do something - develop - project of my life
10 45 - 0123456: Do something \- harder - train - project of my life
12 33 - lunch
...
```

> !!! Task, time, project do not have 'space dash space'. !!!

## Commands

The app has help in command line, read it before use. It always require some command.

```bash
report --help
```

## Config

Near the project (near file app.py) has to be file `config.json` with settings.

Setting that can be setted:

-   hour-report-path - path to file with tasks by hours
-   sqlite-database-path - path to file with database SQLite
-   omit-task - name of tasks that will be skipped
-   output-day-report - where to print result of report, can be 2 type of print (for disabling printing not include that type)
-   minute_round_to - for what number round minutes in the report. Default 25
-   jira - settings related for working with Jira:
    -   server - url to the server with Jira
    -   login - user login to the account
    -   password - user password to the account
    -   issue-key-base - (optional) prefix for all issue key. Default empty array
-   text-indent - indent in the beginning of line for task, type etc
-   dictionary - dictionary with shorter version of origin or reworded (can be used in omit task):
    -   task - only use for task name
    -   kind - only use for kind name, it has to change to alias insided
    -   project - only use for project name, it has to change to alias insided
-   reporting - settings for reporting (have different class for them):
    -   api-url - main url to the reporting api
    -   kinds - dictionary for transformation kinds inside to the reporting, all inside kind's keys can view in command line
    -   login - user login to the account
    -   password - password to the account
    -   projects - dictionary for transformation projects inside to the reporting, all inside project's keys can view in command line
    -   suburl-add-task - related suburl to the some of part
    -   suburl-categories - related suburl to the some of part
    -   suburl-categories-binding - related suburl to the some of part
    -   suburl-corp-struct-items - related suburl to the some of part
    -   suburl-get-report - related suburl to the some of part
    -   suburl-init - related suburl to the some of part
    -   suburl-login - related suburl to the some of part
    -   suburl-logout - related suburl to the some of part
    -   suburl-positions - related suburl to the some of part
    -   suburl-projects - related suburl to the some of part
-   default-type - default type, setted if task does not have, set alias from inside name
-   default-project - default project, setted if task does not have, set alias from inside name

Example:

```json
{
    "hour-report-path": "~/example-hours.txt",
    "omit-task": ["lunch", "break"],
    "outputs-day-report": {
        "console": 1,
        "file": 1
    },
    "minute-round-to": 25,
    "text-indent": "  ",
    "jira": {
        "server": "https://jira.example.domain.com/",
        "login": "test.user",
        "password": "password",
        "issue-key-base": [
            "JRA-"
        ]
    },
    "dictionary": {
        "task": {
            "l": "lunch"
        },
        "type": {},
        "project": {}
    },
    "reporting": {
        "api-url": "https://reporting.example.com/api",
        "kinds": {
            "d": "Develop",
        },
        "login": "test",
        "password": "pass",
        "projects": {
            "bs": "Best Project",
        },
        "suburl-add-task": "example/path",
        "suburl-categories": "example/path",
        "suburl-categories-binding": "example/path",
        "suburl-corp-struct-items": "example/path",
        "suburl-get-report": "example/path",
        "suburl-init": "example/path",
        "suburl-login": "example/path",
        "suburl-logout" : "common/logout",
        "suburl-positions": "example/path",
        "suburl-projects": "example/path",
    },
    "default-type": "Development",
    "default-project": "Project"
}
```

## How it works

Program find tasks, their type and project. Task without project or type get in default name.

Some tasks like lunch can be ommitted. For that purpose they have to be in the config file in ommit array.
Task that has to be ommitted can be anything and have any symbols like another.

## JIRA

You must add 3 required configs for working with Jira: server, login, password.

### Worklog setting

Issue key searches by concatenate base in the settings (default empty string) and any number before double dots. All other information for setting worklog does not need.

## Reporting

Add requests through API.
Firstly do requests for data then it can do what you need.

New requests can be added in the api then used in reporting.
