def parse_common_pattern(summary_text, pattern, group_name):
    value = None
    result = pattern.search(summary_text)
    if result:
        value = int(result.group(group_name).replace(",", ""))
    return value
