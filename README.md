NEWT 2.0
========

NEWT - Nice and Easy Web Toolkit, a ReSTFul API for High Performance Computing.

#Modules
The NEWT 2.0 is organized into 7 different, individually configurable modules. Each module is individually customizable by linking in a new adapter that conforms to the specification.
- **Account**: Gets information about users and groups on the system.
- **Authentication**: Deals with authentication of users.
- **Command**: Runs commands on the system.
- **File**: Create, remove, update, and delete objects in the file system.
- **Job**: Queues, monitors, and modifies jobs on the system.
- **Status**: Checks the status of each system.
- **Stores**: Provides a key-value storage system for applications using NEWT 2.0.

#Initial Setup
NEWT 2.0 is shipped with a local implementation of each of its different modules so it will function out of the box

##Runtime Requirements
- python 2.7.* (https://www.python.org/downloads/)
- pip (http://pip.readthedocs.org/en/latest/installing.html#install-pip)
- libmagic

##Python Package Dependencies
With pip: `pip install -r requirements.txt`. 
Without pip: install these packages manually:

###Required
- Django (https://docs.djangoproject.com/en/dev/topics/install/)
- filemagic (http://filemagic.readthedocs.org/en/latest/guide.html#installation)
- netaddr (https://pythonhosted.org/netaddr/installation.html)
- pyOpenSSL (https://github.com/pyca/pyopenssl)
- pytz (http://pytz.sourceforge.net/#installation)
- requests (http://docs.python-requests.org/en/latest/user/install/)
- wsgiref (https://pypi.python.org/pypi/wsgiref)

###Store Backend Packages
- pymongo (for MongoDB stores) (http://api.mongodb.org/python/current/installation.html)
- redis (for Redis stores) (https://kushal.fedorapeople.org/redis-py/html/user/install.html)

#Getting Started

##Understanding settings.py/local_settings.py
The `settings.py` file (soon to be easier to configure) contains global variables used to edit the functionality of NEWT 2.0. `settings.py` can be edited, but it is recommended to create a `local_settings.py` to overwrite the global variables to preserve the default settings. (See `newt/sample_local_settings.py`)

##Running the server
After changing any settings `./manage.py syncdb`, then run `./manage runserver` to start the server.

#Adapting NEWT
Adapting any module of NEWT to your system is a relatively simple task given experience in Python and Django. In each module, there is an `adapters` folder where new adapters should be placed. The specification for each adapter is given in `<adapter_name>/adapters/template_adapter.py`. 

##Abridged Example (django_adapter for Account)
Say we want to create a new adapter for Account that uses the Django user model to obtain user information. We would first make a copy of `template_adapter.py` into `django_adapter.py`. To add functionality, we see that in the `template_adapter.py` of the Account module, there is a definition for `get_user_info`
```Python
def get_user_info(user_name=None, uid=None):
    """Returns information about the user

    Keyword arguments:
    user_name -- username
    uid -- user id
    """
    pass

```
We would edit the body of the function to make make calls to the Django user model to obtain the information we want:

```Python
def get_user_info(user_name, uid):
    try:
        if uid:
            user = User.objects.get(pk=uid)
        elif user_name:
            user = User.objects.get(username=user_name)
        else:
            raise Exception() # Invalid arguments were given
        user_dict = model_to_dict(user)
        del user_dict["password"]
        return user_dict
    except Exception:
        if user_name:
            return json_response(
                status="ERROR", 
                status_code=404, 
                error="User not found: %s" % user_name
            )
        else:
            return json_response(
                status="ERROR", 
                status_code=404, 
                error="User ID not found: %s" % uid
            )
```
**Note**: This is only one of the two required functions in the adapter; a full example can be seen in `account/adapters/django_adapter.py`.

A couple things to note:

- The function takes in arguments specified by the API url
- The function is allowed to return any Python object, not necessarily a Django response. NEWT automatically wraps the returned values in a Django response.
- To explicitly return a valid API response, use `json_response(status="status", status_code=http_status_code, error="optional_error_message")`.

##Adapter Extras
Adapters also support API calls that are not in the default API endpoints. By adding to `patterns` (near the end of the sample adapter), the `extras_router` (required in every adapter for now) will add them to NEWT.

`patterns` is a tuple list in the form of:
```python
(
    (compiled_regex_exp, associated_function, request_required),
    ...
)
```

**Note**: The compiled_regex_exp must have [named groups](https://docs.python.org/2/howto/regex.html#non-capturing-and-named-groups) corresponding to the arguments of associated_function
**Note**: request_required tells NEWT to pass the request object to your function. If request_required is `True`, the associated_function must have request as the first argument

Example:
```python
patterns = (
    (re.compile(r'/usage/(?P<path>.+)$'), get_usage, False),
    (re.compile(r'/image/(?P<query>.+)$'), get_image, False),
    (re.compile(r'/(?P<path>.+)$'), get_resource, False),
)
```

#Contributors to NEWT 2.0
- [Shreyas Cholia](https://github.com/shreddd)
- [Terence Sun](https://github.com/tsun1215)

