import sys, codecs

class ConfigParser:
	specialValues = {'False': False, 'True': True}

	class ConfigElem:
		pass

	def Parse(self, config):
		inpFile = codecs.open(config, encoding = 'utf-8')
		
		for line in (line_raw.strip('\r\n') for line_raw in inpFile):
			if(not line or line.startswith(';')):
				continue

			(name, path) = line.split('=', 1)
			name = name.strip()
			path = path.strip()

			if (path in self.specialValues):
				path = self.specialValues[path]

			levels = name.split('.')
			curContext = self
			for level in levels[:-1]:
				if(not level in curContext.__dict__):
					setattr(curContext, level, self.ConfigElem())
				curContext = getattr(curContext, level)
				
			setattr(curContext, levels[len(levels) - 1], path)

	def HasField(self, fieldName):
		curContext = self
		for segment in fieldName.split('.'):
			if not segment in curContext.__dict__:
				return False
			curContext = getattr(curContext, segment)

		return True

	def __init__(self, config, shouldBeThere = []):
		self.Parse(config)

		for item in shouldBeThere:
			if not item in self.__dict__:
				sys.stderr.write('Required element "%s" not found in config. Shutting down.\n')
				sys.exit()