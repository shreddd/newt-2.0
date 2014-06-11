
def get_stores():
    """Returns a list of available stores"""
    pass

def create_store(store_name, initial_data=[]):
    """Creates a store with the given store_name and initial_data

    Keyword arguments:
    store_name -- the name of the store
    initial_data -- initial data for the store (optional)
    """
    # Check that store name is unique (or create unique identifier)
    # Create the store
    # Load initial data into the store
    # Return the name of the store/status/objects created
    pass

def delete_store(store_name):
    """Deletes the store with a given store_name

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check privlages of user attempting to delete store
    # Delete store
    # Return the status/output of the operation
    pass

def get_store_contents(store_name):
    """Returns a list containing all the contents of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    # Check privlages of user attempting to access store
    # Get and return contents of the store
    pass

def query_store(store_name, query):
    """Returns the result of querying the given store with query

    Keyword arguments:
    store_name -- the name of the store
    query -- a query string
    """
    # Check privlages of user attempting to acccess store
    # Run query on the given store and return results
    pass

def get_store_perms(store_name):
    """Returns a dictionary of permissions of the store

    Keyword arguments:
    store_name -- the name of the store
    """
    # Return the permissions of the store
    pass

def update_store_perms(store_name, perms):
    """Updates the permissions of the given store with perms

    Keyword arguments:
    store_name -- the name of the store
    perms -- dictionary of the updated permissions
    """
    # Updates the permissions of the store and returns the status
    pass

def store_insert(store_name, data):
    """Inserts data into the store

    Keyword arguments:
    store_name -- the name of the store
    data -- a list of key value pairs to be put in the store
    """
    # Insert the key value pairs into the store
    pass

def store_update(store_name, pair):
    """Updates a certain key-value pair in the store

    Keyword arguments:
    store_name -- the name of the store
    pair -- the updated pair (dict)
    """
    # Set the key of the store to the new value
    pass

def store_get_obj(store_name, obj_id):
    """Gets the value of the specified key in the store 

    Keyword arguments:
    store_name -- the name of the store
    obj_id -- the id at which the objecte is stored in the store
    """
    # Gets the value of the key in the store
    pass

