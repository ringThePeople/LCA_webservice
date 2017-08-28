#encoding:utf-8

from flask import Flask, url_for, render_template, request, redirect, make_response, session
from werkzeug import secure_filename
import os
import workunit
import pandas as pd
from StringIO import StringIO
import numpy as np

UPLOAD_FOLDER = './tmp/'
ALLOWED_EXTENSIONS = set(['csv','tsv','txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		if(request.form['selective_form'] == 'example'):
			fortest = open("lca_framework_test.tsv","r")
			session['uploaded'] = fortest.read()
			fortest.close()
			session['period'] = {'type': 'at_once', 'value': 4}
			session['tool'] = 'genie3'
			resp = make_response(redirect(url_for('display_result'), code=307))
			return resp

		print "====req file====", request.files.keys()
		print "====33====", request.files.getlist("timeseries_data")
		# for file_ in (request.files).keys():
		# 	if allowed_file(request.files[file_].filename):
		# 		file_list.append(request.files[file_])

		file_list = [file_ for file_ in request.files.getlist("timeseries_data") if allowed_file(file_.filename)]
		print "=====file_list" ,file_list

		# print "============file2=======", file2

		try:
			# print "request.form_start", str(request.form['selective_form'])
			#when selective periods chosen
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value'], 'selective_form': str(request.form['selective_form'])}
		except:
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value']}
		tool = 'genie3'
		
		session['uploaded']={}
		session['period'] = period
		session['tool'] = tool

		print "for mun",session['uploaded'] , len(file_list)
		print file_list[0]


		for i,file_ in enumerate(file_list):
			#It should be .stream.read()
			#session['uploaded'].append(file_.stream.read())
			session['uploaded'][int(i)] = file_.stream.read()
			print type(session['uploaded'])


		#print "file_list length", len(file_list)
		# print type(session['uploaded'])
		# print type(session['uploaded'].keys())
		print "uplo", len(session['uploaded'])
		# print session['uploaded']
		print "resp start"
		resp=make_response(redirect(url_for('display_result'), code=307))
		print "resp end"
		return resp

		# if file and allowed_file(file.filename):
		# 	# filename = secure_filename(file.filename)
		# 	# file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# 	session['uploaded'] = []
		# 	session['uploaded'].append(file.stream.read())
		# 	print "===============session type===========\n", type(session)
		# 	print "=============session type[uploaded]============\n", type(session['uploaded'])
			
		# 	session['period'] = period
		# 	session['tool'] = tool
		# 	resp = make_response(redirect(url_for('display_result'), code=307))
		# 	return resp
	return render_template('file_uploader.html')

@app.route('/res', methods=['GET','POST'])
def display_result():
	print "display start"
	if request.method == 'GET':
		return redirect(url_for('upload_file'))
	if request.method == 'POST':
		if 'uploaded' not in session:
			return redirect(url_for('upload_file'))
		
		#Conver String to StringIO in file_list to use pd.read_csv
		print "sessss", session['uploaded']
		print "sssss", len(session['uploaded'])
		#file_io_list = session['uploaded']
		file_io_list = [StringIO(session['uploaded'][file_]) for file_ in session['uploaded'].keys()]
		
		print file_io_list
		if len(file_io_list) ==1:
			print('Using Single Experiment Data')
		elif len(file_io_list) >=2:
			print("Using Multiple Experiments Data")
		elif len(file_io_list) ==0:
			raise ValueError('No file has been assigned')
		else:
			raise ValueError('file_list length is negative !!')

		#_data = session['uploaded'][0]
		# print type(_data)
		# print _data

		# print "StringIO try ======"
		# print pd.read_csv(StringIO(_data),sep="\t")
		
		_options = {'period': session['period'], 'tool': session['tool']}
		print "_options", _options

		# # transpose data
		# xdata = [row.split('\t') for row in _data.split('\n')]
		
		# xdata = xdata[:-1]

		# data = ""
		# print "xdata", xdata
		# print type(xdata[0][5])
		# for cols in range(0, len(xdata[0])):
		# 	data += str(xdata[0][cols].split('\r')[0])
		# 	for rows in range(1, len(xdata)):
		# 		data += "\t"
		# 		data += str(xdata[rows][cols].split('\r')[0])
		# 	data += "\n"
		# print "-----data-----", data
		graphdata, resp = workunit.run(file_io_list, _options)
		
		if not resp: #no error occurred
			return render_template('result_page.html', graphdata=graphdata[0], graphdata2 = graphdata[1], graphdata3 = graphdata[2], graphdata4 = graphdata[3], graphdata5 = graphdata[4], graphdata6 = graphdata[5], graphdata7 = graphdata[6], graphdata8 = graphdata[7], graphdata9 = graphdata[8])
		else:
			return redirect(url_for('upload_file'))

if __name__ == "__main__":
	os.environ['DEBUG'] = "1"
	app.secret_key = 'Shhh, dl zlsms rhdroehldjtjs,dksehlqslek!wjfeofh.'
	# app.run(host='0.0.0.0', port=80, debug=False) 
	app.run(debug=True) 
	