import re, shlex

def valid_url(url):
    pattern = re.compile(r'^([a-zA-Z]+:\/\/)?([a-zA-Z0-9_\-\.]+)(:[0-9]+)?(\/.+)?$')
    return bool(pattern.match(url))

class InvalidRequest(Exception):
    pass

class InvalidPowershell(InvalidRequest):
    pass

class UnkownOption(Exception):
    pass

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"]

class HttpRequest():
    def __init__(self, url, headers={}, method='GET', body=None, auth=None):
        if not url or not valid_url(url):
            raise InvalidRequest('The request must include a valid URL. Given URL: {}'.format(url))
        if not url.startswith('https://'):
            self.url = 'http://' + url
        else:
            self.url = url
        self.headers = headers
        if method not in VALID_METHODS:
            raise InvalidRequest('The given method is invalid. Given method: {}'.format(method))
        self.method = method
        self.body = body
        self.auth = auth
    
    def getCurl(self):
        output = 'curl '
        for header in self.headers:
            output += '-H "{}: {}" '.format(header, self.headers[header])
        
        if self.method != "GET":
            output += '-X "{}" '.format(self.method)
        
        if self.body:
            output += '-d "{}" '.format(self.body.replace('"','\"'))
        
        if self.auth:
            if 'password' in self.auth:
                output += '-u "{}:{}" '.format(self.auth['username'],self.auth['password'])
            else:
                output += '-u "{}" '.format(self.auth['username'])

        return output + self.url     

    def getPowershell(self):
        output = 'Invoke-RestMethod '
        
        if self.headers:
            headersObject = '@{ '
            for header in self.headers:
                headersObject += '"{}"="{}";'.format(header, self.headers[header])
            headersObject += ' } '
            output += '-Headers {}'.format(headersObject)

        if self.method != "GET":
            output += '-Method "{}" '.format(self.method)
        
        if self.body:
            output += '-Body "{}" '.format(self.body.replace('"','`"'))
        
        if self.auth:
            if 'password' in self.auth:
                credentialObject = ('New-Object System.Management.Automation.PSCredential '
                    '-ArgumentList ("{}", (ConvertTo-SecureString '
                    '"{}" -AsPlainText -Force))'
                ).format(self.auth['username'],self.auth['password'])                                
                output += '-Credential ({}) '.format(credentialObject)
            else:
                output += '-Credential ({}) '.format(
                    'Get-Credential -Message "Enter your credentials." -UserName "{}"'.format(self.auth['username'])
                )

        return output + '-Uri ' + self.url        


class InvalidCurl(InvalidRequest):
    pass

class CurlRequest(HttpRequest):
    def __init__(self, curl):
        self.headers = {}
        parts = shlex.split(curl.replace("\r","").replace("\n"," "))
        parts = [part for part in parts if part not in ("", "\\")]
        try:
            if "curl" != parts.pop(0):
                raise InvalidCurl
            while len(parts) > 0:
                part = parts.pop(0).strip()
                if part.startswith("-"):
                    if part in ["-d", "--data"]:
                        self.body = parts.pop(0)
                    elif part in ["-H", "--header"]:
                        header = parts.pop(0)
                        if ":" not in header:
                            raise InvalidCurl
                        header_parts = header.split(":")
                        self.headers[header_parts[0].strip()] = header_parts[1].strip()
                    # elif part in ["-o", "--output"]:
                    #     call["outfile"] = parts.pop(0)
                    elif part in ["-X", "--request"]:
                        method = parts.pop(0)
                        if method not in VALID_METHODS:
                            raise InvalidCurl
                        self.method = method
                    elif part in ["--url"]:
                        self.url = parts.pop(0)
                    elif part in ["-u", "--user"]:
                        self.auth = {}
                        auth = parts.pop(0)
                        if ":" in auth:
                            self.auth["username"], self.auth["password"] = auth.split(":")
                        else:
                            self.auth["username"] = auth
                    else:
                        raise UnkownOption
                elif valid_url(part):
                    self.url = part
        except IndexError:
            raise InvalidCurl
        if not self.url:
            raise InvalidCurl