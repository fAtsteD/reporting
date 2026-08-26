# Create and send report

Program find tasks, their type and project. Task without project or type get in default name.

Some tasks like lunch can be omitted. For that purpose they have to be in the list of skipped tasks
in the configuration. Task that has to be omitted can be anything and have any symbols like another.

## Development

It requires uv installed before.
Initialize project:

```bash
make init
```

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src
```

## File with report

Each line has time, name, type and project they are divided by space-dash-space:

```plain
[hour] [minute] - [name of task] - [name of type] - [name of project]
```

Example:

```plain
09 00 - 0123456: Do something - develop - project of my life
10 45 - 0123456: Do something \- harder - train - project of my life
12 33 - lunch
...
```

> !!! Task, time, project do not have 'space dash space'. !!!

## Commands

The app has help in command line, read it before use. It always require some command.

```bash
reporting --help
```

### Exit codes

Diagnostics go to stderr, results go to stdout, so `reporting show > report.txt` writes only the
report.

| Code | Meaning                                                                                          |
| ---- | ------------------------------------------------------------------------------------------------ |
| 0    | Success                                                                                          |
| 1    | The command failed: nothing to show or send, a task was not sent, the configuration is not valid |
| 2    | The command line is wrong: a missing argument, an unknown command, a date that is not a date     |
| 130  | Interrupted with Ctrl-C                                                                          |

`send` exits 1 when any task fails and prints the reason under the task. `show` and `send` exit 1
when the report does not exist.

## JIRA

Jira requires the server address, login and password in the configuration.

### Worklog setting

Issue key searches by concatenate one of the configured issue key prefixes and any number before double dots. All other information for setting worklog does not need.

## QATestLab Portal

Add requests through API.
Firstly do requests for data then it can do what you need.

New requests can be added in the api then used in the portal.
