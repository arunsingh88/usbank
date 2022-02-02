from dataclasses import dataclass
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json

from flask.wrappers import Response

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def read_json():
    with open('Home_new.json') as f:
        data = json.load(f)
    return data


def payment_read_json():
    with open('Payment.json') as f:
        data = json.load(f)
    return data


def deposit_read_json():
    with open("DepositCheck.json") as f:
        data = json.load(f)
    return data


def moneytransfer_read_json():
    with open("MoneyTransfer.json") as f:
        data = json.load(f)
    return data


def home_signin_json():
    with open('Home_signin.json') as f:
        data = json.load(f)
    return data


def deposit_signin_read_json():
    with open("Deposit Checks02.json") as f:
        data = json.load(f)
    return data


required_json = read_json()
payment_json = payment_read_json()
deposit_json = deposit_read_json()
money_json = moneytransfer_read_json()
signin_json = home_signin_json()
deposit_signin_json = deposit_signin_read_json()
json_data = {"home": required_json, "Digital_Payments": deposit_json, "Protect_Payments": payment_json,
             "Money_Transfer": money_json, "home_login": signin_json, "Digital_Payments_sigin": deposit_signin_json}


def get_nextstep(target, data):
    req_list = []
    source_val = ""
    for key in data['page1'][1]:
        if data['page1'][1][key]["source"] == target:
            req_list.append(data['page1'][1][key])
            source_val = data['page1'][1][key]['source']
    return req_list, source_val


def set_message(response, path, data, current_loc, login_status):
    if data['type'] == "message":
        response["message"] = data["msg"]
        response["payload"]["type"] = data['type']
        response["targetid"] = path[0]['target']
    elif data['type'] == 'options':
        for each_val in data['msg'].split(";"):
            response["payload"]["value"].append({each_val: path[0]['target']})
        response["payload"]["type"] = "buttons"
        response["payload"]["message"] = ""
        response["targetid"] = path[0]['target']
    elif data['type'] == "check":
        for val in path:
            response["payload"]["value"].append(
                {val['condtion']: val['target']})
        response["payload"]["type"] = "buttons"
        response["payload"]["message"] = data['msg']
    elif data['type'] == "end":
        response["payload"]["type"] = data['type']
        response["payload"]["message"] = data['msg']
        if data["msg"] in json_data.keys():
            if current_loc == "Digital_Payments_sigin" and login_status == 'true':
                response = get_nextFlow(
                    json_data["Digital_Payments"], "Digital_Payments", login_status)
            elif login_status == 'true' and data["msg"] == "Digital_Payments":
                response = get_nextFlow(
                    json_data["Digital_Payments_sigin"], "Digital_Payments_sigin", login_status)
            else:
                response = get_nextFlow(
                    json_data[data["msg"]], data['msg'], login_status)
    elif data['type'] == "input":
        response["payload"]["type"] = data['type']
        response["targetid"] = path[0]['target']
    return response


@app.route('/chatbot/deposit', methods=["GET", "POST"])
@cross_origin()
def deposit():
    data = request.get_json()
    response = {"message": "", "payload": {"value": [], "message": ""}}
    if (data):
        path, source = get_nextstep(data['source'], deposit_json)
        if path:
            box_msg = deposit_json["page1"][0][source]
        else:
            box_msg = deposit_json["page1"][0][data['source']]
        response = set_message(response, path, box_msg)
        print(response)
        while True:
            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(response["targetid"], deposit_json)
            if path:
                box_msg = deposit_json["page1"][0][source]
            else:
                box_msg = deposit_json["page1"][0][response["targetid"]]
            response = set_message(response, path, box_msg)

    else:
        path = [deposit_json['page1'][1][deposit_json['page1'][2]]]
        box_msg = deposit_json["page1"][0][path[0]["source"]]
        response = set_message(response, path, box_msg)
        while True:

            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(response["targetid"], deposit_json)
            response = set_message(
                response, path, deposit_json["page1"][0][source])
    return jsonify({"response": response})


@app.route('/chatbot/payment', methods=["GET", "POST"])
@cross_origin()
def payment():
    data = request.get_json()
    response = {"message": "", "payload": {"value": [], "message": ""}}
    if (data):
        path, source = get_nextstep(data['source'], payment_json)
        if path:
            box_msg = payment_json["page1"][0][source]
        else:
            box_msg = payment_json["page1"][0][data['source']]
        response = set_message(response, path, box_msg)
        while True:
            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(response["targetid"], payment_json)
            if path:
                box_msg = payment_json["page1"][0][source]
            else:
                box_msg = payment_json["page1"][0][response["targetid"]]
            response = set_message(response, path, box_msg)

    else:
        path = [payment_json['page1'][1][payment_json['page1'][2]]]
        box_msg = payment_json["page1"][0][path[0]["source"]]

        response = set_message(response, path, box_msg)
        while True:

            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(response["targetid"], payment_json)
            response = set_message(
                response, path, payment_json["page1"][0][source])
    return jsonify({"response": response})


@app.route('/chatbot', methods=["POST"])
@cross_origin()
def chatbot():
    data = request.get_json()
    response = {"message": "", "payload": {
        "value": [], "message": ""}, "topic": ""}
    print(data)
    if data and data["source"]:
        current_loc, login_status = data['topic'], data["login"]
        topic_json = json_data[data['topic']]
        path, source = get_nextstep(data['source'], topic_json)
        if path:
            box_msg = topic_json["page1"][0][source]
        else:
            box_msg = topic_json["page1"][0][data['source']]
        response = set_message(response, path, box_msg,
                               current_loc, login_status)
        while True:
            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(response["targetid"], topic_json)
            if path:
                box_msg = topic_json["page1"][0][source]
            else:
                box_msg = topic_json["page1"][0][response["targetid"]]
            response = set_message(
                response, path, box_msg, current_loc, login_status)
        if not response["topic"]:
            response["topic"] = data['topic']
    else:
        if data['login'] == 'true':
            print('I am here')
            location = "home_login"
        else:
            location = "home"
        current_loc, login_status = location, data["login"]
        path = [json_data[location]['page1'][1]
                [json_data[location]['page1'][2]]]
        box_msg = json_data[location]["page1"][0][path[0]["source"]]
        response = set_message(response, path, box_msg,
                               current_loc, login_status)
        while True:
            if response["payload"]["type"] in ["end", "buttons"]:
                break
            path, source = get_nextstep(
                response["targetid"], json_data[location])
            response = set_message(
                response, path, json_data[location]["page1"][0][source], current_loc, login_status)
        response["topic"] = location
        if data['login'] == 'false':
            response["payload"] = {}
    if "targetid" in response:
        response.pop("targetid")

    return jsonify({"response": response})


def get_nextFlow(req_json_data, topic, status):
    response = {"message": "", "payload": {"value": [], "message": ""}}
    path = [req_json_data['page1'][1][req_json_data['page1'][2]]]
    box_msg = req_json_data["page1"][0][path[0]["source"]]

    response = set_message(response, path, box_msg, topic, status)
    while True:

        if response["payload"]["type"] in ["end", "buttons"]:
            break
        path, source = get_nextstep(response["targetid"], req_json_data)
        response = set_message(
            response, path, req_json_data["page1"][0][source], topic, status)
    response["topic"] = topic
    return response


# main driver function
if __name__ == '__main__':
    app.run()
