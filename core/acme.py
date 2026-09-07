# NOTE(vanya):
# ACME (Automatic Certificate Management Environment) is outlined in: https://rfc-editor.org/rfc/rfc8555



import urllib.request
import json

from . import p256


DIRECTORY_URL = "https://acme-staging-v02.api.letsencrypt.org/directory"


# with urllib.request.urlopen(DIRECTORY_URL) as response:
#     directory = json.load(response)


# print(json.dumps(directory, indent=4))
