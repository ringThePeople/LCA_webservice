#encoding:utf-8

from flask import Flask, url_for, render_template, request, redirect, make_response, session
from werkzeug import secure_filename
import os
import workunit

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

		file = request.files['timeseries_data']
		try:
			# print "request.form_start", str(request.form['selective_form'])
			#when selective periods chosen
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value'], 'selective_form': str(request.form['selective_form'])}
		except:
			period = {'type': request.form['period_info'], 'value': request.form['period_info_value']}
		tool = request.form['tool-name']
		print "tool name: ",tool
		if file and allowed_file(file.filename):
			# filename = secure_filename(file.filename)
			# file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			
			session['uploaded'] = file.stream.read()
			session['period'] = period
			session['tool'] = tool
			resp = make_response(redirect(url_for('display_result'), code=307))
			return resp
	return render_template('file_uploader.html')

@app.route('/res', methods=['GET','POST'])
def display_result():
	if request.method == 'GET':
		return redirect(url_for('upload_file'))
	if request.method == 'POST':
		if 'uploaded' not in session:
			return redirect(url_for('upload_file'))
		_data = session['uploaded']
		_options = {'period': session['period'], 'tool': session['tool']}
		print "_options", _options
		graphdata, resp = workunit.run(_data, _options)
		
		if not resp: #no error occurred
			return render_template('result_page.html', graphdata=graphdata[0], graphdata2 = graphdata[1], graphdata3 = graphdata[2], graphdata4 = graphdata[3], graphdata5 = graphdata[4], graphdata6 = graphdata[5], graphdata7 = graphdata[6], graphdata8 = graphdata[7], graphdata9 = graphdata[8])
		else:
			return redirect(url_for('upload_file'))

if __name__ == "__main__":
	os.environ['DEBUG'] = "1"
	app.secret_key = 'Shhh, dl zlsms rhdroehldjtjs,dksehlqslek!wjfeofh.'
	app.run(host='0.0.0.0', port=80, debug=False) 