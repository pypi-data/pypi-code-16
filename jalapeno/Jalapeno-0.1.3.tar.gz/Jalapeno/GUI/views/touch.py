from flask import Blueprint,render_template,request
from Jalapeno.lib.jalop_markdown import Jalo_render
from Jalapeno.lib.siteMgr import Site,SITE_DIR
import os

SITES_PAGE_FOLDER = SITE_DIR+os.sep+'Pages'+os.sep


touch = Blueprint('touch',__name__)

@touch.route('/touch')
def show():
	return render_template('editor.html')


@touch.route('/touch/editor')
def editor():
	return render_template('editor.html')

@touch.route('/touch/render',methods =['GET','POST'])
def render():
	data = request.get_data().decode()
	return Jalo_render(data)

@touch.route('/touch/open',methods =['GET','POST'])
def file_open():
	doc_name,doc_folder = request.form.getlist("data[]", type=str)
	doc_path = SITES_PAGE_FOLDER+doc_folder+os.sep+doc_name+'.md'
	try:
		f = open(doc_path,'r')
		doc_content = f.read()
		f.close()
		return doc_content
	except FileNotFoundError:
		print('Target Folder does not exist')
		return 'Target Folder does not exist'

@touch.route('/touch/save',methods =['GET','POST'])
def file_save():
	doc_name,doc_content= request.form.getlist("data[]", type=str)
	doc_path = SITES_PAGE_FOLDER+'Draft'+os.sep+doc_name+'.dft'
	try:
		f = open(doc_path,'w')
		f.write(doc_content)
		f.close()
		print('success')
		return 'success'
	except FileNotFoundError:
		print('Target Folder does not exist')
		return 'Target Folder does not exist'





@touch.route('/touch/finish',methods =['GET','POST'])
def file_finish():
	# doc_name,doc_folder,doc_content = request.get_data().decode()
	doc_name,doc_folder,doc_content= request.form.getlist("data[]", type=str)
	doc_path = SITES_PAGE_FOLDER+doc_folder+os.sep+doc_name+'.md'
	draft_path = SITES_PAGE_FOLDER+'Draft'+os.sep+doc_name+'.dft'
	print(doc_path)
	try:
		f = open(doc_path,'w')
		f.write(doc_content)
		f.close()
		os.remove(draft_path)
		print('success')
		return 'success'
	except FileNotFoundError:
		print('Target Folder does not exist')
		return 'Target Folder does not exist'
