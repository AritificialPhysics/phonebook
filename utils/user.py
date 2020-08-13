"""Module for user table management."""

import contacts
import hashlib
import sqlite3


# opening database and setting connection
conn = sqlite3.connect('material.db')
c = conn.cursor()


def _user_auth(username):
	"""Returns true if the username already exists in the users table."""
	login = [username]
	encrypted_credentials = _encryption(login)
	# User table doesn't exist on first run, so silence the error from sqlite
	# that the table doesn't exist
	try:
		sql = c.execute("SELECT username FROM users WHERE username = ?", encrypted_credentials)
	except:
		pass

	row = c.fetchone()
	if row is None:
		return False
	else:
		return True


def _user_auth(username, password):
	"""Returns true if the username and password both exist in the database."""
	login_credentials = [username, password]
	encrypted_credentials = _encrpytion(login_credentials)

	sql = c.execute('''SELECT * FROM users
					WHERE username = ? AND password = ?''', encrypted_credentials)

	record = c.fetchone()
	if record is None:
		return False
	else:
		return True
	

def _input_credentials():
	"""Inputs and returns username and password."""
	username = input('Username: ')
	password = input('Password: ')

	return (username, password)


def _scrub(table_name):
	"""Sanitzes input for database"""
	return ''.join( chr for chr in table_name if chr.isalnum() or chr == '_' )


def _encryption(login_details):
	"""Return the login credential in sha256 encrypted format."""
	encrypt_login_details = list()
	for credential in login_details:
		encrypt_login_details.append(hashlib.sha256(credential.encode()).hexdigest())
	return tuple(encrypt_login_details)


def add_user():
	"""Adds user to database if doesn't exist and create a contacts table for him.
	Returns a string indicating the status
	"""
	username, password = _input_credentials()

	if _user_exists(username):
		return "The user already exists"
	else:
		#Add user to users table
		c.execute("""CREATE TABLE IF NOT EXISTS users( 
			username VARCHAR(256) NOT NULL,
			password VARCHAR(256) NOT NULL);
		""")
		encrypted_credentials = _encryption([username, password])
		c.execute("INSERT INTO users VALUES (?,?);", encrypted_credentials)
		conn.commit()

		#Create contacts table for user. Name: contacts_username
		#Scrubing the username.
		tablename = _scrub('contacts_' + username)
		c.execute(f"""CREATE TABLE {tablename} (
			name VARCHAR(255) NOT NULL,
			phno VARCHAR(20) NOT NULL,
			email VARCHAR(255) NOT NULL);
			""")
		
		conn.commit()
		
		return "User successfully added"


def remove_user():
	"""Removes a user and associated contact table from the database.
	Returns a string indicating the status
	"""
	username, password = _input_credentials()

	if _user_auth(username, password):
		#Remove user from users table
		encrypted_username = _encryption([username])
		c.execute("DELETE FROM users WHERE username = ?", encrypted_username)
		conn.commit()

		#Remove users contacts table
		tablename = _scrub('contacts_' + username)
		c.execute(f"DROP TABLE {tablename} ")
		return "User successfully removed"
	else:
		return "User not found"


def select_user():
	"""Selects a user for current contact operations.
	Returns a string indicating the status
	"""
	username, password = _input_credentials()

	if _user_auth(username, password):
		contacts._username = username
		return "User successfully selected"
	else:
		return "User not found"