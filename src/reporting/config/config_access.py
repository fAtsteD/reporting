import json
import types
import typing
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from reporting.config.exceptions import ConfigError
from reporting.config.models import KeyKind, ResolvedKey, RootConfig


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)


def get_value(root: RootConfig, key: str) -> Any:
    resolved = resolve(key)
    value: Any = root

    for field_name in resolved.field_names:
        value = getattr(value, field_name)

    if resolved.kind is KeyKind.DICT_ENTRY:
        return value.get(resolved.entry_key)

    return value


def iterate_values(root: RootConfig) -> list[tuple[str, Any, str]]:
    values: list[tuple[str, Any, str]] = []
    _collect_values(root, [], values)
    values.sort(key=lambda item: item[0])

    return values


def resolve(key: str) -> ResolvedKey:
    if not key:
        raise ConfigError("Configuration key is required")

    segments = key.split(".")
    model: type[BaseModel] = RootConfig
    aliases: list[str] = []
    field_names: list[str] = []

    for index, segment in enumerate(segments):
        field_name, field_info = _find_field(model, segment)
        field_names.append(field_name)
        aliases.append(field_info.alias or field_name)
        annotation = _unwrap_optional(field_info.annotation)
        origin = typing.get_origin(annotation)
        is_last = index == len(segments) - 1
        rest = segments[index + 1 :]

        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            if is_last:
                return ResolvedKey(aliases=aliases, field_names=field_names, kind=KeyKind.SECTION)

            model = annotation
            continue

        if origin is dict:
            value_type = typing.get_args(annotation)[1]

            if is_last:
                return ResolvedKey(
                    aliases=aliases,
                    field_names=field_names,
                    kind=KeyKind.DICT_FIELD,
                    value_type=value_type,
                )

            if len(rest) > 1:
                raise ConfigError(f'Configuration key "{key}" is too deep')

            return ResolvedKey(
                aliases=aliases,
                entry_key=rest[0],
                field_names=field_names,
                kind=KeyKind.DICT_ENTRY,
                value_type=value_type,
            )

        if not is_last:
            raise ConfigError(f'Configuration key "{key}" is too deep')

        if origin is list:
            return ResolvedKey(
                aliases=aliases,
                field_names=field_names,
                kind=KeyKind.LIST_FIELD,
                value_type=typing.get_args(annotation)[0],
            )

        return ResolvedKey(
            aliases=aliases,
            field_names=field_names,
            kind=KeyKind.SCALAR_FIELD,
            value_type=annotation,
        )

    raise ConfigError(f'Unknown configuration key "{key}"')


def set_value(data: dict[str, Any], key: str, raw_value: str) -> None:
    resolved = resolve(key)

    if resolved.kind is KeyKind.SECTION:
        raise ConfigError(f'"{key}" is a group of settings. Set one of the settings inside it')

    if resolved.kind is KeyKind.DICT_FIELD:
        raise ConfigError(f'"{key}" is a group of values. Set one entry, for example "{key}.<name>"')

    container = _ensure_container(data, resolved.aliases[:-1])
    leaf_alias = resolved.aliases[-1]
    value = _coerce_value(resolved.value_type, raw_value)

    if resolved.kind is KeyKind.LIST_FIELD:
        items = container.get(leaf_alias)

        if not isinstance(items, list):
            items = []
            container[leaf_alias] = items

        if value not in items:
            items.append(value)

        return

    if resolved.kind is KeyKind.DICT_ENTRY:
        entries = container.get(leaf_alias)

        if not isinstance(entries, dict):
            entries = {}
            container[leaf_alias] = entries

        entries[resolved.entry_key] = value

        return

    container[leaf_alias] = value


def unset_value(data: dict[str, Any], key: str, raw_value: str = "") -> None:
    resolved = resolve(key)

    if raw_value and resolved.kind is not KeyKind.LIST_FIELD:
        raise ConfigError(f'"{key}" is not a list, so a single value cannot be removed from it')

    parent_aliases = resolved.aliases[:-1]
    container = _find_container(data, parent_aliases)
    leaf_alias = resolved.aliases[-1]

    if container is None:
        if raw_value:
            raise ConfigError(f'"{raw_value}" is not in {key}')

        return

    if resolved.kind is KeyKind.LIST_FIELD and raw_value:
        items = container.get(leaf_alias)
        value = _coerce_value(resolved.value_type, raw_value)

        if not isinstance(items, list) or value not in items:
            raise ConfigError(f'"{raw_value}" is not in {key}')

        items.remove(value)
    elif resolved.kind is KeyKind.DICT_ENTRY:
        entries = container.get(leaf_alias)

        if isinstance(entries, dict):
            entries.pop(resolved.entry_key, None)
    else:
        container.pop(leaf_alias, None)

    _prune_empty(data, resolved.aliases)


def _coerce_value(value_type: Any, raw_value: str) -> Any:
    if _unwrap_optional(value_type) is str:
        return raw_value

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value


def _collect_values(model: BaseModel, prefix: list[str], values: list[tuple[str, Any, str]]) -> None:
    for field_name, field_info in type(model).model_fields.items():
        alias = field_info.alias or field_name
        value = getattr(model, field_name)
        path = prefix + [alias]

        if isinstance(value, BaseModel):
            _collect_values(value, path, values)
            continue

        values.append((".".join(path), value, field_info.description or ""))


def _ensure_container(data: dict[str, Any], aliases: list[str]) -> dict[str, Any]:
    container = data

    for alias in aliases:
        child = container.get(alias)

        if not isinstance(child, dict):
            child = {}
            container[alias] = child

        container = child

    return container


def _find_container(data: dict[str, Any], aliases: list[str]) -> dict[str, Any] | None:
    container = data

    for alias in aliases:
        child = container.get(alias)

        if not isinstance(child, dict):
            return None

        container = child

    return container


def _find_field(model: type[BaseModel], alias: str) -> tuple[str, FieldInfo]:
    for field_name, field_info in model.model_fields.items():
        if (field_info.alias or field_name) == alias:
            return field_name, field_info

    available = ", ".join(sorted(info.alias or name for name, info in model.model_fields.items()))
    raise ConfigError(f'Unknown configuration key "{alias}". Available keys here: {available}')


def _prune_empty(data: dict[str, Any], aliases: list[str]) -> None:
    for index in range(len(aliases), 0, -1):
        parent = _find_container(data, aliases[: index - 1])

        if parent is None:
            return

        child = parent.get(aliases[index - 1])

        if isinstance(child, dict) and not child:
            del parent[aliases[index - 1]]


def _unwrap_optional(annotation: Any) -> Any:
    origin = typing.get_origin(annotation)

    if origin is typing.Union or origin is types.UnionType:
        args = [argument for argument in typing.get_args(annotation) if argument is not type(None)]

        if len(args) == 1:
            return args[0]

    return annotation
