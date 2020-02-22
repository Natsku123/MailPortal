from mysql.connector import connect, errorcode, Error
from modules.utils import get_config

config = get_config()


def db(f):
    """
    Wrap database connection for database functions.
    :param f: function to be wrapped
    :return:
    """
    def wrap(*args, **kwargs):
        try:
            cnx = connect(**config['database'])
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return_value = {"status": "Error: Unable to access database with given user and password."}
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                return_value = {"status": "Error: Database doesn't exist."}
            else:
                return_value = {"status": "Error: " + str(err)}
        else:
            return_value = f(cnx, *args, **kwargs)
            cnx.close()
        return return_value
    return wrap


@db
def create_user(cnx, user):
    """
    Creates a new user to the virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :param user: user data in this order: email, password, domain_id
    :return: status message and id
    """
    cursor = cnx.cursor()

    add_user = ("INSERT INTO `virtual_users` (`email`, `password`, `domain_id`) VALUES ('%s', ENCRYPT('%s', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), %s);")

    try:
        cursor.execute(add_user, user)
        cnx.commit()
        user_id = cursor.lastrowid
        return_value = {"status": "success", "user_id": user_id}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def create_domain(cnx, domain):
    """
    Creates a new domain to virtual_domains table.
    :param cnx: database connection from 'db' wrapper
    :param domain: domain data in this order: name
    :return: status message and id
    """
    cursor = cnx.cursor()

    add_domain = ("INSERT INTO `virtual_domains` (`name`) VALUES ('%s');")

    try:
        cursor.execute(add_domain, domain)
        cnx.commit()
        domain_id = cursor.lastrowid
        return_value = {"status": "success", "domain_id": domain_id}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def create_alias(cnx, alias):
    """
    Creates a new alias to virtual_aliases table.
    :param cnx: database connection from 'db' wrapper
    :param alias: alias data in this order: domain_id, source, destination
    :return: status message and id
    """
    cursor = cnx.cursor()

    add_alias = ("INSERT INTO `virtual_aliases` (`domain_id`, `source`, `destination`) VALUES ('%s', '%s', '%s');")

    try:
        cursor.execute(add_alias, alias)
        cnx.commit()
        alias_id = cursor.lastrowid
        return_value = {"status": "success", "alias_id": alias_id}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def update_user(cnx, user_id, email=None, password=None):
    """
    Updates user in virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :param user_id: user's id that is going to be updated
    :param email: new email if exists
    :param password: new password if exists
    :return: status message
    """
    cursor = cnx.cursor()

    if email and password:
        update_query = ("UPDATE `virtual_users` SET `password`=ENCRYPT('%s', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), `email`='%s' WHERE `id`=%s;")
        update_data = (password, email, user_id)
    elif email:
        update_query = ("UPDATE `virtual_users` SET `email`='%s' WHERE `id`=%s;")
        update_data = (email, user_id)
    elif password:
        update_query = ("UPDATE `virtual_users` SET `password`=ENCRYPT('%s', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))) WHERE `id`=%s;")
        update_data = (password, user_id)
    else:
        return {'status': 'No changes to be made.'}

    try:
        cursor.execute(update_query, update_data)
        cnx.commit()
        return_value = {"status": "success"}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def update_alias(cnx, alias_id, source=None, destination=None):
    """
    Updates alias in virtual_aliases table.
    :param cnx: database connection from 'db' wrapper
    :param alias_id: alias' id that is going to be updated
    :param source: new source email if exists
    :param destination: new destination email if exists
    :return: status message
    """
    cursor = cnx.cursor()

    if source and destination:
        update_query = ("UPDATE `virtual_aliases` SET `source`='%s', `destination`='%s' WHERE `id`=%s;")
        update_data = (source, destination, alias_id)
    elif source:
        update_query = ("UPDATE `virtual_aliases` SET `source`='%s' WHERE `id`=%s;")
        update_data = (source, alias_id)
    elif destination:
        update_query = ("UPDATE `virtual_aliases` SET `destination`='%s' WHERE `id`=%s;")
        update_data = (destination, alias_id)
    else:
        return {'status': 'No changes to be made.'}

    try:
        cursor.execute(update_query, update_data)
        cnx.commit()
        return_value = {"status": "success"}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def delete_user(cnx, user_id):
    """
    Deletes user from virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :param user_id: user's id that is going to be deleted
    :return: status message
    """
    cursor = cnx.cursor()

    delete_query = ("DELETE FROM `virtual_users` WHERE `id`='%s';")

    try:
        cursor.execute(delete_query, (user_id,))
        cnx.commit()
        return_value = {"status": "success"}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def delete_alias(cnx, alias_id):
    """
    Deletes user from virtual_aliases table.
    :param cnx: database connection from 'db' wrapper
    :param alias_id: alias' id that is going to be deleted
    :return: status message
    """
    cursor = cnx.cursor()

    delete_query = ("DELETE FROM `virtual_aliases` WHERE `id`='%s';")

    try:
        cursor.execute(delete_query, (alias_id,))
        cnx.commit()
        return_value = {"status": "success"}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def handle_login(cnx, username, password):
    """
    Check if user exists in virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :param username: username of user
    :param password: password of user
    :return: True or False (if exists or not)
    """
    cursor = cnx.cursor(dictionary=True)

    login_query = ("SELECT * FROM `virtual_users` WHERE `email`='%s' AND `password`=ENCRYPT('%s', `password`) LIMIT 1;")
    login_data = (username, password)

    try:
        cursor.execute(login_query, login_data)
        if cursor.rowcount == 1:
            return_value = True
        else:
            return_value = False
    except Error as err:
        return_value = False
    finally:
        cursor.close()

    return return_value


@db
def get_users(cnx):
    """
    Get all users from virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :return: list of users
    """
    cursor = cnx.cursor(dictionary=True)

    users_query = ("SELECT id, email FROM `virtual_users`;")

    try:
        cursor.execute(users_query)
        return_value = {'status': "success", "users": []}
        for row in cursor:
            return_value['users'].append(row)
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value


@db
def get_user(cnx, email):
    """
    Get one user from virtual_users table.
    :param cnx: database connection from 'db' wrapper
    :param email: email of user
    :return: user
    """
    cursor = cnx.cursor(dictionary=True)

    user_query = ("SELECT id, email FROM `virtual_users` WHERE `email`='%s' LIMIT 1;")

    try:
        cursor.execute(user_query, (email,))
        return_value = {'status': "success", "user": cursor[0]}
    except Error as err:
        return_value = {"status": "Error: " + str(err)}
    finally:
        cursor.close()

    return return_value
