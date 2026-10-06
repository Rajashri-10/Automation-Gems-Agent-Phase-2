def validate_record(record: dict) -> tuple[bool, str]:

    name = record.get("name", "").strip()
    description = record.get(
        "description",
        "",
    ).strip()
    instructions = record.get(
        "instructions",
        "",
    ).strip()

    if not name:
        return False, "Agent name is empty."

    if not description:
        return False, "Description is empty."

    if not instructions:
        return False, "Instructions are empty."

    return True, "Valid"


def validate_records(records: list[dict]):
    valid_records = []
    invalid_records = []

    for record in records:

        is_valid, message = validate_record(
            record
        )

        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append(
                {
                    **record,
                    "error": message,
                }
            )

    return valid_records, invalid_records