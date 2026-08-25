from pydantic import ValidationError


def describe(error: ValidationError) -> str:
    problems = []

    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        problems.append(f"{location}: {item['msg']}" if location else item["msg"])

    return "\n".join(problems)
