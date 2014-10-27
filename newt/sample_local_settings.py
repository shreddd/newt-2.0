# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'newtdb.sqlite', # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '', # Set to empty string for default.
    }
}

# NEWT Settings
NEWT_HOST = 'YOUR_HOST_HERE'
NEWT_COOKIE_LIFETIME=43200  # How long (in seconds) the user should stay signed in
MYPROXY_SERVER = 'YOUR_MYPROXY_SERVER'  # MyProxy server URL/IP for file transfers
NEWT_CONFIG = {
    'SYSTEMS': [    # Systems to be managed by NEWT
        {'NAME': 'SYSTEM_1', 'HOSTNAME': 'SYSTEM_HOST_URL' },
        {'NAME': 'SYSTEM_2', 'HOSTNAME': 'SYSTEM_HOST_URL' },
        {'NAME': 'SYSTEM_3', 'HOSTNAME': 'SYSTEM_HOST_URL' },
        {'NAME': 'SYSTEM_4', 'HOSTNAME': 'SYSTEM_HOST_URL' },
    ],
    # Each module should be linked to an adapter (and models if necessary).
    'ADAPTERS': {
        'STATUS': {
            'adapter': 'status.adapters.ping_adapter',
            'models': "",
        },
        'FILE': {
            'adapter': 'file.adapters.localfile_adapter',
            'models': "",
        }, 
        'AUTH': {
            'adapter': 'auth.adapters.myproxy_adapter',
            'models': "auth.adapters.myproxy_models",
        },
        'COMMAND': {
            'adapter': 'command.adapters.exec_adapter',
            'models': "",
        },
        'STORES': {
            'adapter': 'stores.adapters.dbstore_adapter',
            'models': "stores.adapters.dbstore_models",
        },
        'ACCOUNT': {
            'adapter': 'account.adapters.django_adapter',
            'models': "",
        },
        'JOB': {
            'adapter': 'job.adapters.unix_adapter',
            'models': "",
        },
    },
}