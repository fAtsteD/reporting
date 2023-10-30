from config_app import Config
from models.kind import Kind


class KindService:
    """
    Orchestrate kind operations
    """

    def add(self, alias: str, name: str) -> Kind:
        """
        Create/update kind and return it
        """
        kind = Config.sqlite_session.query(Kind).filter(Kind.alias == alias).first()

        if kind is None:
            kind = Kind(alias=alias, name=name)
            Config.sqlite_session.add(kind)
        else:
            kind.name = name

        Config.sqlite_session.commit()

        return kind

    def text_all_kinds(self) -> str:
        """
        Create text with all kinds and their data
        """
        kinds = Config.sqlite_session.query(Kind).all()
        text = ""

        for kind in kinds:
            text += f"{kind}\n"

        return text
