"""Module for user table management."""

from . import contacts
from . import helper
import hashlib
import sqlite3
import re


# opening database and setting connection
conn = sqlite3.connect('material.db')
c = conn.cursor()


def _user_exists(username):
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
	encrypted_credentials = _encryption(login_credentials)

	# If table lookup fails, most likely cause is that table doesn't exist, in which case
	# simply returns false
	try:
		sql = c.execute('''SELECT * FROM users
					WHERE username = ? AND password = ?''', encrypted_credentials)
	except:
		return False

	record = c.fetchone()
	if record is None:
		return False
	else:
		return True
	

def _create_input_credentials():
	"""Inputs, checks and returns username and password. Applicable for creating user name
	and password only.
	"""
	username = input('\nUsername: ')

	# checking if username is less than 4 return false
	if len(username) < 4:
		print('Username is too small:')
		return False

	# password prototype
	print('Password prototype...\n')
	print('At least 1 lower case [a - z] alphabet..')
	print('At least 1 upper case [A - Z] alphabet..')
	print('At least 1 number or digit [0 - 9]..')
	print('At least 1 special character like [@, #, $, &, +, -, *, ?, .]..\n')
	password = input('Password: ')

	flag = True
	while True:

		if len(password) < 8:
			flag = False
			break
		elif not re.search('[a - z]', password):
			flag = False
			break
		elif not re.search('[A - Z]', password):
			flag = False
			break
		elif not re.search('[0 - 9]', password):
			flag = False
			break
		elif not re.search('[@#$&+-*?.]', password):
			flag = False
			break

	if flag == False:
		print('Entered Password is not valid:')
		# Doesn't break tuple unpacking in add_user()
		return False
	else:
		# if all good return username & password
		return (username, password)


def _input_credentials():
	"""Inputs and returns username and password."""
	username = print('Username: ')
	password = print('Password: ')

	return (username, password)


def _encryption(login_details):
	"""Return the login credential in sha256 encrypted format."""
	encrypt_login_details = list()
	for credential in login_details:
		encrypt_login_details.append(hashlib.sha256(credential.encode()).hexdigest())
	return tuple(encrypt_login_details)


def add_user():
	"""Adds user to database if doesn't exist and create a contacts table for him."""
	print('Add user')
	credentials = _create_input_credentials()

	if isinstance(credentials, bool):
		return False
	else:
		username, password = credentials

	if _user_exists(username):
		return False
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
		tablename = helper.scrub('contacts_' + username)
		c.execute(f"""CREATE TABLE {tablename} (
			name VARCHAR(255) NOT NULL,
			phno VARCHAR(20) NOT NULL,
			email VARCHAR(255) NOT NULL);
			""")
		
		conn.commit()

		return True


def remove_user():
	"""Removes a user and associated contact table from the database."""
	print('Delete user')
	username, password = _input_credentials()

	if _user_auth(username, password):
		#Remove user from users table
		encrypted_username = _encryption([username])
		c.execute("DELETE FROM users WHERE username = ?", encrypted_username)
		conn.commit()

		#Remove users contacts table
		tablename = helper.scrub('contacts_' + username)
		c.execute(f"DROP TABLE {tablename} ")
		return True
	else:
		return False


def select_user():
	"""Selects a user for current contact operations."""
	print('Select user')
	username, password = _input_credentials()

	if _user_auth(username, password):
		contacts._set_tablename(username)
		return True
	else:
		return False