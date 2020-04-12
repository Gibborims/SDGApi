from flask import Flask, request
app = Flask(__name__)





@app.route("/")
def home():
    return "Hello, Flask!"

@app.route('/api/v1/on-covid-19/<incoming_data>')
def estimator_api_data(incoming_data):
    if request.method == 'GET':
        return incoming_data
    else:
        return "3. Sorry, the request method is not a POST request."


@app.route('/api/v1/on-covid-19', methods = ['POST'])
def raw_estimator_api(format_type):
    if request.method == 'POST':
        data = request.data
        return redirect(url_for('estimator_api_data', incoming_data = data))
    else:
        return "2. Sorry, the request method is not a POST request."


@app.route('/api/v1/on-covid-19/<format_type>', methods = ['POST'])
def the_estimator_api(format_type):
    if request.method == 'POST':
        data = request.data
        if format_type == 'json':
            return data
        elif format_type == 'xml':
            return data
        else:
            return data
    else:
        return "Sorry, the request method is not a POST request."














if __name__ == '__main__':
    app.run(debug = True)

