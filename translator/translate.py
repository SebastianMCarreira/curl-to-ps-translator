import re, shlex

VALID_CURL_OPTIONS = ["-d", "--data", "-H", "--header", "-o", "--output", "-X", 
                        "--request", "--url", "-u", "--user"]
VALID_CURL_FLAGS = ["-k", "--insecure"]
VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"]

class InvalidCurl(Exception):
    pass

class UnkownOption(Exception):
    pass

def valid_url(url):
    pattern = re.compile(r'^([a-zA-Z]+:\/\/)?([a-zA-Z0-9_\-\.]+)(:[0-9]+)?(\/.+)?$')
    return bool(pattern.match(url))

def get_call_from_curl(curl):
    parts = shlex.split(curl.replace("\r","").replace("\n"," "))
    parts = [part for part in parts if part != "" and part != "\\"]
    try:
        if "curl" != parts.pop(0):
            raise InvalidCurl

        call = {
            "url": None,
            "headers": []
        }
        while len(parts) > 0:
            part = parts.pop(0)
            if part.startswith("-"):
                if part in ["-d", "--data"]:
                    call["body"] = parts.pop(0)
                elif part in ["-H", "--header"]:
                    header = parts.pop(0)
                    if ":" not in header:
                        raise InvalidCurl
                    header_parts = header.split(":")
                    header = {
                        "name": header_parts[0].strip(),
                        "value": header_parts[1].strip()
                        }
                    call["headers"].append(header)
                elif part in ["-o", "--output"]:
                    call["outfile"] = parts.pop(0)
                elif part in ["-X", "--request"]:
                    method = parts.pop(0)
                    if method not in VALID_METHODS:
                        raise InvalidCurl
                    call["method"] = method
                elif part in ["--url"]:
                    call["url"] = parts.pop(0)
                elif part in ["-k", "--insecure"]:
                    call["insecure"] = True
                else:
                    raise UnkownOption
            elif valid_url(part):
                call["url"] = part
    except IndexError:
        raise InvalidCurl
    if call["url"] == None:
        raise InvalidCurl
    return call
    