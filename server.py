#!/usr/bin/python

import sys, getopt, json
import socket

class Server(object):
	def __init__(self, argv):
		try:
			opts, args = getopt.getopt(argv, "hu:")
		except getopt.GetoptError:
			help()

		users = []
		names = []
		for opt, arg in opts:
			if opt == "-h":
				help()
			elif opt == "-u":
				names.append(arg)
				users.append(User(arg))

		self.s = socket.socket()
		self.tally = Tally(users)
		self.c = None

		print 'Created users:', ', '.join(names)

	def run(self):
		self.s = socket.socket()
		host = socket.gethostname()
		port = 1337
		self.s.bind((host, port))

		print 'Listening for connections'
		self.s.listen(5)
		while True:
			self.c, addr = self.s.accept()
			self.handle_conn()

	def handle_conn(self):
		recv = json.loads(self.c.recv(1024))
		cmd = recv['command']
		args = recv['args']

		if cmd == 'add':
			self.tally.add_to(args[0])
			msg = args[0] + ' is now on ' + str(self.tally.get_brews(args[0])) + ' brews'
			self.c.send(msg)
			print 'DEBUG:', msg
		elif cmd == 'vote':
			self.tally.set_voted(args[0])

			if self.tally.all_voted():
				msg = 'Everyone\'s now ready for a brew!'
				print 'DEBUG:', msg
				self.c.send(msg);
				self.tally.reset_votes()
			else:
				msg = 'Thanks for your vote!'
				print 'DEBUG:', msg
				self.c.send(msg);
		elif cmd == 'reset':
			self.tally.reset_votes()

		self.c.close()

"""User object for storing the status of each user"""
class User(object):
	def __init__(self, name):
		self._name = name
		self._tally = 0
		self._voted = False

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		self._name = value

	@property
	def tally(self):
		return self._tally

	@property
	def voted(self):
		return self._voted

	@voted.setter
	def voted(self, value):
		self._voted = value

	def add_to_tally(self, increment=1):
		self._tally += increment

"""Tally object for storing a list of users and handling tally operations"""
class Tally(object):
	def __init__(self, users):
		self.users = users

	def has_user(self, person):
		for user in self.users:
			if user.name == person:
				return True
		return False

	def get_user(self, person):
		for user in self.users:
			if user.name == person:
				return user
		return False

	def add_to(self, person, increment=1):
		if not self.has_user(person):
			return False
		self.get_user(person).add_to_tally(increment)

	def get_brews(self, person):
		if not self.has_user(person):
			return False
		return self.get_user(person).tally

	def set_voted(self, person, voted=True):
		if not self.has_user(person):
			return False
		self.get_user(person).voted = voted

	def reset_votes(self):
		for user in self.users:
			user.voted = False

	def all_voted(self):
		allVoted = True
		for user in self.users:
			if user.voted != True:
				allVoted = False
		return allVoted

def help():
	print 'Usage:'
	print '\tpython server.py [-u user1] [-u user2]'
	print ''
	print 'Arguments:'
	print '\t-u\tAn arbitrary amount of users that you want to add to the brew round'
	sys.exit(1)

if __name__ == '__main__':
	a = Server(sys.argv[1:])
	a.run()
