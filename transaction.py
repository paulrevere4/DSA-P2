"""
Theo Browne & Paul Revere
Distributed Systems and Algorithms 2016
Project 2
transaction.py
"""
# ==============================================================================
#
class Transaction(object):
	"""
	Object representation of a "transaction", these are messaged between
	processes
	"""
    # ==========================================================================
    # Setup member variables
    #
	def __init__(self, value, zxid = None):

		if (zxid == None):
			# If no zxid is passed, then we are "unpacking" a packed transaction
			self.value = value[0]
			self.epoch = int(value[1])
			self.counter = int(value[2])
		else:
			# Set value, epoch, and counter from value and zxid if zxid exists
			self.value = value
			self.epoch = zxid[0]
			self.counter = zxid[1]

	# ==========================================================================
    # Packs transaction into a list to be sent through serializer
    #
	def pack(self):
		return [self.value, str(self.epoch), str(self.counter)]

	# ==========================================================================
    # For printing
    #
	def __repr__(self):
		return str(self.pack())

	# ==========================================================================
    # For priority queue placement
    #
	def __lt__(self, other):
		if self.epoch < other.epoch:
			return True
		else:
			if self.epoch == other.epoch and self.counter < other.counter:
				return True
			else:
				return False
