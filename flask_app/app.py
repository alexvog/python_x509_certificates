from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/csr-create.html', methods=['GET', 'POST'])
def csr_create():
    if request.method == 'POST':
        csr_data = {
            "csr_data": {
                "common_name": request.form['common_name'],
                "country": request.form['country'],
                "state": request.form['state'],
                "locality": request.form['locality'],
                "organization": request.form['organization'],
                "organizational_unit": request.form['organizational_unit']
            },
            "key_size": int(request.form['key_size'])
        }

        response = requests.post('http://localhost:1880/create-csr', json=csr_data)
        result = response.json()
        pkeyURL = result['pkeyURL']
        csrURL = result['csrURL']

        return render_template('csr-result.html', pkeyURL=pkeyURL, csrURL=csrURL)
    return render_template('csr-create.html')

@app.route('/csr-sign.html', methods=['GET', 'POST'])
def csr_sign():
    if request.method == 'POST':
        #csr_file = request.files['csr']
        
        input_type = request.form.get('input_type')

        if input_type == 'file':
            csr_file = request.files['csr_file']
            csr = csr_file.read()

        elif input_type == 'text':
            csr = request.form['csr_text']
        
        
        not_valid_before = request.form['not_valid_before']
        not_valid_after = request.form['not_valid_after']

        data = {
            'csr': csr,
            'not_valid_before': not_valid_before,
            'not_valid_after': not_valid_after
        }

        response = requests.post('http://localhost:1880/sign-csr', data=data)
        result = response.json()
        crtURL = result['crt']

        return render_template('crt-result.html', crtURL=crtURL)
    return render_template('csr-sign.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
