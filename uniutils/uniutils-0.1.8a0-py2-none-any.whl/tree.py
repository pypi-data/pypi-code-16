
__version__ = '0.1'

__RNAME__ = ['Rnd', 1]

from subprocess import check_call
import sys, os
from PIL import Image

class ListStream:
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)
    def __enter__(self):
        sys.stdout = self
        return self
    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__

class tnode:
	
	def __init__(self, name="root", label='',random=False):
		if random:
			self.name = '_'.join(str(x) for x in __RNAME__)
			__RNAME__[1] += 1
		else:
			self.name = name
		self.label = label

		self.parent = None
		self.first_child = None
		self.next_sibling = None

	def append_to_parent(self, parent, label=''):
		self.next_sibling = parent.first_child
		parent.first_child = self
		self.parent = parent
		if label is not '':
			self.label = label


	def __str__(self):
		s = "name: {0}\nid: {1}\nparent: {2}\nlabel: {3}\nchild: {4}\nnext_sibling: {5}\n"
		return s.format(self.name, id(self), id(self.parent), self.label, id(self.first_child), id(self.next_sibling))


class tree:

	@staticmethod
	def __str_tree_rec(current_node):
		if (current_node == None):
			return
		tree.__str_tree_rec(current_node.first_child)
		tree.__str_tree_rec(current_node.next_sibling)
		if current_node.parent != None:
			print("\t\"{0}\" -> \"{1}\" [label=\"{2}\"];".format(
				current_node.parent.name, 
				current_node.name, 
				current_node.label))

	@staticmethod
	def str_tree(root, name='g'):
		with ListStream() as x:
			print("digraph %s {" % str(name))
			tree.__str_tree_rec(root);
			print("}")
		return ''.join(x.data)

	@staticmethod
	def set_random_pattern(pattern):
		__RNAME__[0] = str(pattern)

	@staticmethod
	def plot_tree(str, save_in=False, save_out=False, in_name='indot', out_name='out'):
		in_name += '.dot'
		out_name += '.png'
		with open(in_name, 'w+') as infile:
			for line in str:
				infile.write(line)
		check_call(['dot','-Tpng',in_name,'-o',out_name])
		img = Image.open(out_name)
		img.show()
		if not save_in:
			os.remove(in_name)
		if not save_out:
			os.remove(out_name)
