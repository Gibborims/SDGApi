from flask import Flask, request, redirect, url_for
app = Flask(__name__)


import math

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
        data = request.data
        return data
    else:
        return "3. Sorry, the request method is not a POST request."


@app.route('/api/v1/on-covid-19')
def raw_estimator_api():
    if request.method == 'POST':
        data = request.data
        return data
        # return redirect(url_for('estimator_api_data', incoming_data = data))
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
            return "This format parameter is not allowed."
    else:
        return "Sorry, the request method is not a POST request."














if __name__ == '__main__':
    app.run(debug = True)

