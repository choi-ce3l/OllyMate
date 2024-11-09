import re

def preprocessing_product_name(text):
    patterns = [
        r'\[.*?\]|\(.*?\)|\d+ml.*'

    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    text = re.sub(r'\s+', ' ', text).strip()
    return text