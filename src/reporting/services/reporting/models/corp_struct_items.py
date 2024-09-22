class CorpStructItems:
    """
    Hold corpStructItems and related function
    It has corpStructItems from request

    CorpStructItem:
    {
        "alias": str,
        "deleted": bool,
        "description": str,
        "groupId": int,
        "id": int,
        "name": str,
        "parentId": int,
        "typeAlias": str,
        "typeId": int
    }
    """

    def __init__(self, corp_struct_items: list) -> None:
        """
        Init corpStructItems object
        """
        self._corp_struct_items = corp_struct_items

    def get_by_id(self, id: int) -> dict | None:
        """
        Return corpStructItem dictionary by alias
        """
        if len(self._corp_struct_items) == 0:
            return None

        for corp_struct_item in self._corp_struct_items:
            if corp_struct_item["id"] == id:
                return corp_struct_item

        return None

    def get_by_alias(self, alias: str) -> dict | None:
        """
        Return corpStructItem dictionary by alias
        """
        if len(self._corp_struct_items) == 0:
            return None

        for corp_struct_item in self._corp_struct_items:
            if corp_struct_item["alias"] == alias:
                return corp_struct_item

        return None
