from django.contrib.auth.middleware import RemoteUserMiddleware


# customising the RemoteUserMiddleware to get the HTTP header that openshift adds
class ProxyRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_X_REMOTE_USER'
