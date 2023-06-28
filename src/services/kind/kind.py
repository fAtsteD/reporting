from config_app import config
from models.kind import Kind


class KindService():
    """
    Orchestrate kind CRUD and other operations
    """

    def add(self, alias: str, name: str) -> Kind:
        """
        Create new kind and return it
        """
        kind = config.sqlite_session.query(Kind).filter(
            Kind.alias == alias
        ).first()

        if kind is None:
            kind = Kind(alias=alias, name=name)
            config.sqlite_session.add(kind)
        else:
            kind.name = name

        config.sqlite_session.commit()

        return kind

    def text_all_kinds(self) -> str:
        """
        Create text with all kinds and their data
        """
        kinds = config.sqlite_session.query(Kind).all()
        text = ""

        for kind in kinds:
            text += f"{kind}\n"

        return text
