"""Module provides various helper functions for main script and other modules."""

import sys
import time
import os

def clear_screen():
	"""Clears the screen after switching menu"""
	if os.name == 'nt':
		_ = os.system('cls')
	else:
		_ = os.system('clear')

def trigger_exit():
	"""Initiates the exit sequence."""
	print('\nExiting phonebook!')
	time.sleep(0.3)
	sys.exit(1)


def scrub(table_name):
	"""Sanitizes input for database query"""
	return ''.join( chr for chr in table_name if chr.isalnum() or chr == '_' )