from config_app import Config
from models.project import Project


class ProjectService:
    """
    Orchestrate project operations
    """

    def add(self, alias: str, name: str) -> Project:
        """
        Create/update project and return it
        """
        project = Config.sqlite_session.query(Project).filter(Project.alias == alias).first()

        if project is None:
            project = Project(alias=alias, name=name)
            Config.sqlite_session.add(project)
        else:
            project.name = name

        Config.sqlite_session.commit()

        return project

    def text_all_projects(self) -> str:
        """
        Create text with all kinds and their data
        """
        projects = Config.sqlite_session.query(Project).all()
        text = ""

        for project in projects:
            text += f"{project}\n"

        return text
