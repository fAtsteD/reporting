from config_app import config
from models.project import Project


class ProjectService:
    """
    Orchestrate project operations
    """

    def add(self, alias: str, name: str) -> Project:
        """
        Create/update project and return it
        """
        project = config.sqlite_session.query(Project).filter(Project.alias == alias).first()

        if project is None:
            project = Project(alias=alias, name=name)
            config.sqlite_session.add(project)
        else:
            project.name = name

        config.sqlite_session.commit()

        return project

    def text_all_projects(self) -> str:
        """
        Create text with all kinds and their data
        """
        projects = config.sqlite_session.query(Project).all()
        text = ""

        for project in projects:
            text += f"{project}\n"

        return text
