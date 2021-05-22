import dateutil.parser


class config:
    """
    Hold all config vars

    One config for app, so all vars static.
    """
    # Input
    input_file_hours = ""

    # Output
    outputs_day_report = []
    file_type_print = 1
    console_type_print = 1
    output_file_day = ""
    text_indent = "  "

    # Tasks
    skip_tasks = []
    minute_round_to = 25

    # Jira
    jira = {
        "use_jira": False,
        "issue_key_base": ""
    }

    # Parameters for program
    work_day_hours = dateutil.parser.parse("08:00")
