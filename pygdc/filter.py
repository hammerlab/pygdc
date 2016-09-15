def and_filter(*ops):
    return {
        "op": "and",
        "content": [op for op in ops if op]
    }

def equals_filter(field, value):
    return {
        "op": "=",
        "content": {
            "field": field,
            "value": value
        }
    }