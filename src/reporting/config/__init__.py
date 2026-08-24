from reporting.config import config_file
from reporting.config.models import RootConfig

current: RootConfig = config_file.load()
app = current.app
dictionary = current.dictionary
jira = current.jira
qatestlab_portal = current.qatestlab_portal


def reload() -> None:
    global app, current, dictionary, jira, qatestlab_portal
    current = config_file.load()
    app = current.app
    dictionary = current.dictionary
    jira = current.jira
    qatestlab_portal = current.qatestlab_portal
