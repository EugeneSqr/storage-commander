from requests.auth import AuthBase

class CxAuth(AuthBase):
    def __init__(self, token):
        self._token = token

    def __call__(self, request):
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request
