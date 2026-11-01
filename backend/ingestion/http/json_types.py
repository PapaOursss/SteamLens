from collections.abc import Mapping

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type QueryParams = Mapping[str, str | int]
