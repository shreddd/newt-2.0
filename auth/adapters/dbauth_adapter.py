from django.contrib.auth import authenticate, login, logout

# We just use the default backend for this adapter

def is_logged_in(request):
    if (request.user is not None) and (request.user.is_authenticated()):
        output=dict(auth=True,
                    username=request.user.username,
                    session_lifetime=request.session.get_expiry_age(),
                    newt_sessionid=request.session.session_key)
    else:
        output=dict(auth=False,
                    username=None,
                    session_lifetime=0,
                    newt_sessionid=None)
    return output


def get(request):
    return is_logged_in(request)


def post(request):

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)

    return is_logged_in(request)

def delete(request):
    logout(request)

    return is_logged_in(request)