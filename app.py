from flask import Flask, request, redirect, url_for, Response, make_response
app = Flask(__name__)


import math
import json
import ast

def json2xml(json_obj, line_padding=""):
    result_list = list()

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))

        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("%s<%s>" % (line_padding, tag_name))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("%s</%s>" % (line_padding, tag_name))

        return "\n".join(result_list)

    return "%s%s" % (line_padding, json_obj)



def estimator(data):
  output_data = {}
  impact = {}
  severeImpact = {}

  reported_cases = data["reportedCases"]
  currently_infected = covid19ImpactEstimator(reported_cases)
  severe_currently_infected = covid19SevereImpactEstimator(reported_cases)

  period_type = data["periodType"]
  duration = data["timeToElapse"]
  total_hospital_beds = data["totalHospitalBeds"]
  avg_daily_income = data["region"]["avgDailyIncomeInUSD"]
  avg_daily_income_populase = data["region"]["avgDailyIncomePopulation"]

  infections_time = infectionsByRequestedTime(currently_infected, period_type, duration)
  severe_infections_time = infectionsByRequestedTime(severe_currently_infected, period_type, duration)

  case_by_time = severeCasesByRequestedTime(infections_time)
  severe_case_by_time = severeCasesByRequestedTime(severe_infections_time)

  hosp_beds_by_reqtime = hospitalBedsByRequestedTime(total_hospital_beds, case_by_time)
  severe_hosp_beds_by_reqtime = hospitalBedsByRequestedTime(total_hospital_beds, severe_case_by_time)

  icu_by_reqtime = casesForICUByRequestedTime(infections_time)
  severe_icu_by_reqtime = casesForICUByRequestedTime(severe_infections_time)

  ventilators_by_reqtime = casesForVentilatorsByRequestedTime(infections_time)
  severe_ventilators_by_reqtime = casesForVentilatorsByRequestedTime(severe_infections_time)

  dollars_in_flight = dollarsInFlight(infections_time, avg_daily_income_populase, avg_daily_income, period_type, duration)
  dollars_in_flight_severe = dollarsInFlight(severe_infections_time, avg_daily_income_populase, avg_daily_income, period_type, duration)


  impact["currentlyInfected"] = currently_infected
  impact["infectionsByRequestedTime"] = infections_time
  impact["severeCasesByRequestedTime"] = math.trunc(case_by_time)
  impact["hospitalBedsByRequestedTime"] = hosp_beds_by_reqtime
  impact["casesForICUByRequestedTime"] = math.trunc(icu_by_reqtime)
  impact["casesForVentilatorsByRequestedTime"] = math.trunc(ventilators_by_reqtime)
  impact["dollarsInFlight"] = dollars_in_flight

  severeImpact["currentlyInfected"] = severe_currently_infected
  severeImpact["infectionsByRequestedTime"] = severe_infections_time
  severeImpact["severeCasesByRequestedTime"] = math.trunc(severe_case_by_time)
  severeImpact["hospitalBedsByRequestedTime"] = severe_hosp_beds_by_reqtime
  severeImpact["casesForICUByRequestedTime"] = math.trunc(severe_icu_by_reqtime)
  severeImpact["casesForVentilatorsByRequestedTime"] = math.trunc(severe_ventilators_by_reqtime)
  severeImpact["dollarsInFlight"] = dollars_in_flight_severe

  output_data["data"] = data
  output_data["impact"] = impact
  output_data["severeImpact"] = severeImpact


  # print(output_data)
  return output_data


def covid19ImpactEstimator(reported_cases):
  return (reported_cases * 10)


def covid19SevereImpactEstimator(reported_cases):
  return (reported_cases * 50)


def daysFactor(days):
  # return (days % 3)
  return math.trunc(days/3)


def dayNormalizer(period_type, duration):
  days = 0
  if (period_type == "days"):
    days = int(duration)
  elif (period_type == "weeks"):
    days = int(duration) * 7
  elif (period_type == "months"):
    days = int(duration) * 30
  else:
    days

  return int(days)



def infectionsByRequestedTime(currently_infected, period_type, duration):
  days = dayNormalizer(period_type, duration)
  return (currently_infected * (2 ** (daysFactor(days))))


def severeCasesByRequestedTime(infections_by_time):
  return (0.15 * infections_by_time)


def required_available_beds(total_hospital_beds):
  return (0.35 * total_hospital_beds)


def hospitalBedsByRequestedTime(total_hospital_beds, severe_case_by_time):
  req_available_beds = required_available_beds(total_hospital_beds)
  return math.trunc(req_available_beds - severe_case_by_time)


def casesForICUByRequestedTime(infections_by_time):
  return (0.05 * infections_by_time)


def casesForVentilatorsByRequestedTime(infections_by_time):
  return (0.02 * infections_by_time)


def dollarsInFlight(infections_by_time, avg_daily_income_populase, avg_daily_income, period_type, duration):
  days = dayNormalizer(period_type, duration)
  return math.trunc((infections_by_time * avg_daily_income_populase * avg_daily_income) / days)





@app.route("/")
def home():
    return "Hello, Flask!"

@app.route('/api/v1/on-covid-19/', methods = ['POST'])
def estimator_api_data():
    if request.method == 'POST':
        # data = request.data
        # print(ast.literal_eval(request.data.decode("utf-8")))
        data = ast.literal_eval(request.data.decode("utf-8"))
        # return estimator(data)
        resp = make_response(estimator(data))
        resp.headers['Content-type'] = 'application/json; charset=utf-8'
        return resp
    else:
        return "3. Sorry, the request method is not a POST request."


@app.route('/api/v1/on-covid-19', methods = ['POST'])
def raw_estimator_api():
    if request.method == 'POST':
        # data = request.data
        data = ast.literal_eval(request.data.decode("utf-8"))
        # return estimator(data)
        resp = make_response(estimator(data))
        resp.headers['Content-type'] = 'application/json; charset=utf-8'
        return resp
        # return redirect(url_for('estimator_api_data', incoming_data = data))
    else:
        return "1. Sorry, the request method is not a POST request."




@app.route('/api/v1/on-covid-19/json', methods = ['POST'])
def the_estimator_api_json():
    if request.method == 'POST':
        data = ast.literal_eval(request.data.decode("utf-8"))
        # print(data)
        # return estimator(data)
        resp = make_response(estimator(data))
        resp.headers['Content-type'] = 'application/json; charset=utf-8'
        return resp
    else:
        resp = make_response({"resp_desc":"3. Sorry, the request method is not a POST request."})
        resp.headers['Content-type'] = 'application/json; charset=utf-8'
        return resp




@app.route('/api/v1/on-covid-19/xml', methods = ['POST'])
def the_estimator_api_xml():
    if request.method == 'POST':
        data = ast.literal_eval(request.data.decode("utf-8"))
        # print(data)
        # return estimator(data)

        resp = make_response(json2xml(estimator(data)))
        resp.headers['Content-type'] = 'application/xml; charset=utf-8'
        return resp
    else:
        resp = make_response('<resp_desc>3. Sorry, the request method is not a POST request.</resp_desc>')
        resp.headers['Content-type'] = 'application/xml; charset=utf-8'
        return resp


# @app.route('/api/v1/on-covid-19/<format_type>', methods = ['POST'])
# def the_estimator_api(format_type):
#     if request.method == 'POST':
#         if format_type == 'json':
#             data = ast.literal_eval(request.data.decode("utf-8"))
#             print(data)
#             r = Response(response=estimator(data), status=200, mimetype="application/json")
#             r.headers["Content-Type"] = "text/json; charset=utf-8"
#             print(r)
#             return r
            
#         elif format_type == 'xml':
#             data = ast.literal_eval(request.data.decode("utf-8"))
#             print(data)
#             r = Response(response=estimator(data), status=200, mimetype="application/xml")
#             r.headers["Content-Type"] = "text/xml; charset=utf-8"
#             print(r)
#             return r
#             # return json2xml(estimator(data)) #Response(estimator(data), mimetype='text/xml')
#         else:
#             return "This format parameter is not allowed."
#     else:
#         return "Sorry, the request method is not a POST request."














if __name__ == '__main__':
    app.run(debug = True)

