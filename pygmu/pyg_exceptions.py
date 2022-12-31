class PygException(Exception):
	"""Base class for all pygmu exceptions"""
	pass

class ChannelCountMismatch(PygException):
	"""Raised when a processing element is handed the wrong nubmer of channels"""
	pass

class FrameRateMismatch(PygException):
	"""Raised when a processing element is handed an incompatible frame rate"""
	pass

class IndefiniteExtent(PygException):
	"""Raised when a processing element is handed an indefinite extent"""
	pass

