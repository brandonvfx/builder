import sys
import unittest

sys.path.insert(0, '..')
from api import Cabinet
from api.blueprint import Blueprint

class CorrectBlueprint(Blueprint):
	class Meta:
		name = 'correct_blueprint'
	# end class
# end class


class InCorrectBlueprint(Blueprint):
	class Meta:
		version = (1,1,1)
	# end class
# end class

class TestCabinet(unittest.TestCase):

	def setUp(self):
		self.cab = Cabinet()
	# end def setUp

	def test_correct_register(self):
		self.cab.register(CorrectBlueprint)
		self.assertEqual(self.cab._Cabinet__blueprints, {'correct_blueprint':CorrectBlueprint})
	# end def test_correct_register

	def test_missing_name_register(self):
		self.assertRaises(RuntimeError, self.cab.register,InCorrectBlueprint)
	# end def test_correct_register


	def test_register_default(self):
		self.cab.register(CorrectBlueprint, True)
		self.assertEqual(self.cab._Cabinet__blueprints, {'correct_blueprint':CorrectBlueprint, 'default':CorrectBlueprint})
	# end def test_correct_register

	def test_keys(self):
		self.cab.register(CorrectBlueprint, True)
		self.assertEqual(sorted(self.cab.keys()), ['correct_blueprint', 'default'])
	# end def test_correct_register

	def test_contains(self):
		self.cab.register(CorrectBlueprint, True)
		self.assertTrue('correct_blueprint' in self.cab)
		self.assertFalse('missing' in self.cab)
	# end def test_correct_register

	def test_attribute(self):
		self.cab.register(CorrectBlueprint, True)
		self.assertEqual(self.cab.correct_blueprint, CorrectBlueprint)
		self.assertEqual(self.cab.default, CorrectBlueprint)
	# end def test_correct_register
# end class

if __name__ == '__main__':
	unittest.main()
	

