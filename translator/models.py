import re, shlex
from flask import abort

def valid_url(url):
    pattern = re.compile(r'^([a-zA-Z]+:\/\/)?([a-zA-Z0-9_\-\.]+)(:[0-9]+)?(\/.+)?$')
    return bool(pattern.match(url))

class InvalidRequest(Exception):
    pass

class UnkownOption(Exception):
    pass

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"]

class HttpRequest():
    def __init__(self, url, headers={}, method='GET', body=None, auth=None):
        self.setUrl(url)
        self.headers = headers
        self.setMethod(method)
        self.body = body
        self.auth = auth

    def setUrl(self, url):
        if not url or not valid_url(url):
            raise InvalidRequest('The request must include a valid URL. Given URL: {}'.format(url))
        if not url.startswith('https://'):
            self.url = 'http://' + url
        else:
            self.url = url
    
    def setMethod(self, method):
        if method not in VALID_METHODS:
            raise InvalidRequest('The given method is invalid. Given method: {}'.format(method))
        self.method = method
    
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
        self.originalCommand = curl

        self.method = "GET"
        self.headers = {}
        self.url = None
        self.auth = None
        self.body = None
        parts = shlex.split(curl.replace("\r","").replace("\n"," "))
        parts = [part for part in parts if part not in ("", "\\")]
        try:
            if "curl" != parts.pop(0):
                raise InvalidCurl('The command must start with "curl"')
            while len(parts) > 0:
                part = parts.pop(0).strip()
                if part.startswith("-"):
                    if part in ["-d", "--data"]:
                        self.body = parts.pop(0)
                    elif part in ["-H", "--header"]:
                        header = parts.pop(0)
                        if ":" not in header:
                            raise InvalidCurl('The headers must be key-values pairs separated by a colon ":"')
                        header_parts = header.split(":")
                        self.headers[header_parts[0].strip()] = header_parts[1].strip()
                    # elif part in ["-o", "--output"]:
                    #     call["outfile"] = parts.pop(0)
                    elif part in ["-X", "--request"]:
                        self.setMethod(parts.pop(0))
                    elif part in ["--url"]:
                        self.setUrl(parts.pop(0))
                    elif part in ["-u", "--user"]:
                        self.auth = {}
                        auth = parts.pop(0)
                        if ":" in auth:
                            self.auth["username"], self.auth["password"] = auth.split(":")
                        else:
                            self.auth["username"] = auth
                    else:
                        raise UnkownOption('Given option "{}" not recognized.'.format(part))
                else:
                    self.setUrl(part)
        except IndexError:
            raise InvalidCurl
        if not self.url:
            raise InvalidCurl('The command must include an URI.')
    
    def getCurl(self):
        return self.originalCommand


class InvalidPowershell(InvalidRequest):
    pass

class PowershellRequest(HttpRequest):
    def __init__(self, powershell):
        self.originalCommand = powershell

        self.method = "GET"
        self.headers = {}
        self.url = None
        self.auth = None
        self.body = None
        if "@{" in powershell:
            psObjects = re.findall('@{[^}]*}',powershell)
            for psObj in psObjects:
                psObj_no_whitespace = "".join(shlex.split(psObj.replace('"','\\\"').replace("'","\\\'")))
                powershell = powershell.replace(psObj, psObj_no_whitespace)
        parts = shlex.split(powershell.replace("\r","").replace("\n"," "))
        parts = [part for part in parts if part not in ("", "\\")]
        try:
            if "Invoke-RestMethod" != parts.pop(0):
                raise InvalidPowershell('The command must start with "Invoke-RestMethod"')
            while len(parts) > 0:
                part = parts.pop(0).strip()
                if part.startswith("-"):
                    if part == '-Body':
                        self.body = parts.pop(0)
                    elif part == '-Headers':
                        headers = parts.pop(0).replace('@{','').replace('}','').split(";")
                        for header in headers:
                            if header:
                                key, value = header.split('=')
                                self.headers[key] = value
                    # elif part in ["-o", "--output"]:
                    #     call["outfile"] = parts.pop(0)
                    elif part == '-Method':
                        self.setMethod(parts.pop(0))
                    elif part == '-Uri':
                        self.setUrl(parts.pop(0))
                    elif part == '-Credential':
                        abort(501,'Parsing credentials from a PowerShell command is not implemented.')
                    else:
                        raise UnkownOption('Given option "{}" not recognized.'.format(part))
        except IndexError:
            raise InvalidPowershell
        if not self.url:
            raise InvalidPowershell('The command must include an URI.')

    def getPowershell(self):
        return self.originalCommand