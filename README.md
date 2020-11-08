# Create and send report

## File with report

Each line has time, name of task and project they are divided by space-dash-space:

> [hour] [minute] - [name of task] - [name of project]

Example:

> 09 00 - 0123456: Do something - project of my life  
> 10 45 - 0123456: Do something harder - project of my life  
> 12 33 - lunch

> !!! Task, time, project do not have space dash space. !!!

## Result of transformation

> !!! Program round time in the result to 0.25 hour. !!!

## Config

Near the project (near file app.py) has to be file config.json with settings.

Setting that can be setted:

- hour-report-path - path to file with tasks by hours
- day-report-path - path to file where will be write tasks by project
- omit-task - name of tasks that will be skipped
- output-day-report - where to print result of report, can be 2 type of print (for disabling printing not include that type)

Example:

```json
{
    "hour-report-path": "~/example-hours.txt",
    "day-report-path": "~/example-day-report.txt",
    "omit-task": [
        "lunch",
        "break"
    ],
    "outputs-day-report": [
        "console": 2,
        "file": 1
    ]
}
```

## How it works

Program find tasks and their project. Task without project get in default project.

Some tasks like lunch can be ommitted. For that purpose they have to be in the config file in ommit array.
Task that has to be ommitted can be anything and have any symbols like another.
