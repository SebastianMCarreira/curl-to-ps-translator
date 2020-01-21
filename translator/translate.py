VALID_CURL_OPTIONS = ["-d", "--data", "-H", "--header", "-k", "--insecure", 
                        "-o", "--output", "-X", "--request", "--url", "-u", "--user"]

def valid_curl(text):
    parts = text.split(" ")
    parts = [part for part in parts if part != ""]
    if "curl" != parts.pop(0):
        return False
    for part in parts:
        if part.startswidth("-"):
            if part not in VALID_CURL_OPTIONS:
                return False
    return True