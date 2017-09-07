#encoding:utf-8

from flask import Flask, url_for, render_template, request, redirect, make_response, session
from werkzeug import secure_filename
import os
import workunit
import pandas as pd
from StringIO import StringIO
import numpy as np

# UPLOAD_FOLDER = './tmp/'
UPLOAD_FOLDER = './uploaded_data/'
ALLOWED_EXTENSIONS = set(['csv','tsv','txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':

		file_list = [file_ for file_ in request.files.getlist("timeseries_data") if allowed_file(file_.filename)]
		
		try:
			#when selective periods chosen
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value'], 'selective_form': str(request.form['selective_form']), 'ntree': request.form['ntree_value'], 'threshold': request.form['threshold_value']}
		except:
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value'], 'ntree': request.form['ntree_value'], 'threshold': request.form['threshold_value']}
		tool = 'genie3'
		print "========width=======", request.form['width']
		print "==========heigh=======", request.form['height']
		session['size'] = (request.form['width'], request.form['height'])
		session['uploaded']=[]
		session['period'] = period
		session['tool'] = tool

		print "for mun",session['uploaded'] , len(file_list)
		print file_list[0]

		for i,file_ in enumerate(file_list):
			print "asdasdasd", type(file_)
			# It should be .stream.read()
			# session['uploaded'].append(file_.stream.read())
			# session['uploaded'][int(i)] = file_.stream.read()
			# print type(session['uploaded'])
			fname = secure_filename(file_.filename)
			uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], fname)
			file_.save(uploaded_file)
			session['uploaded'].append(uploaded_file)
			file_.close()
			

		resp=make_response(redirect(url_for('display_result'), code=307))
		return resp

	return render_template('file_uploader.html')

@app.route('/res', methods=['GET','POST'])
def display_result():
	print "display start"
	if request.method == 'GET':
		return redirect(url_for('upload_file'))
	if request.method == 'POST':
		print "session in display", session
		if 'uploaded' not in session:
			return redirect(url_for('upload_file'))
		
		#Conver String to StringIO in file_list to use pd.read_csv
		print "sessss", session['uploaded']
		print "sssss", len(session['uploaded'])
		filename_list = session['uploaded']

		print filename_list
		if len(filename_list) ==1:
			print('Using Single Experiment Data')
		elif len(filename_list) >=2:
			print("Using Multiple Experiments Data")
		elif len(filename_list) ==0:
			raise ValueError('No file has been assigned')
		else:
			raise ValueError('file_list length is negative !!')

		
		_options = {'period': session['period'], 'tool': session['tool'], 'size': session['size']}
		print "_options", _options

		graphdata, resp = workunit.run(filename_list, _options)
		
		if not resp: #no error occurred
			return render_template('result_page.html', graphdata=graphdata)
		else:
			return redirect(url_for('upload_file'))

if __name__ == "__main__":
	os.environ['DEBUG'] = "1"
	app.secret_key = 'Shhh, dl zlsms rhdroehldjtjs,dksehlqslek!wjfeofh.'
	# app.run(host='0.0.0.0', port=80, debug=False, threaded=True) 
	app.run(debug=True) 
	