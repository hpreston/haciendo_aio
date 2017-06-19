#!/usr/bin/env python
"""
Author: Hank Preston <hank.preston@gmail.com>
Date: March 26, 2017
GitHub: http://github.com/hpreston/haciendo_aio
Lab: http://github.com/hpreston/haciendo_lab

Haciendo is a simple application built as a fun demonstration
and lab exercise for application refactoring.

The point of the lab is to take an application originally
written to be "monolithic", with all elements of the application
running on a single server instance, and "refactor" it to be
containerized and built in a micro-service fashion.

This is the api server element of the application.  Written in
Python and leveraging Flask and FlaskRestful it provides a basic
REST API to retrieve job requests and process them.  It leverages
other APIs including:

    - “Powered by Yandex.Translate” http://translate.yandex.com/.
    - SMS Messaging Services from Tropo via the haciendo_sms service
"""

from flask import Flask, make_response, request, jsonify
from flask_restful import Resource, Api, reqparse
import requests
import json

app = Flask(__name__)
api = Api(app)

# Setup expected API Arguments
api_parser = reqparse.RequestParser()

# The line to translate
api_parser.add_argument("line",
                     type=str,
                     help="The English line to translate"
                     )
# The phone number to send message to
api_parser.add_argument("phonenumber",
                     type=str,
                     help="The phone number to SMS the message to."
                     )

# API key for Yandex Translation Service
yandex_key = ""

def translate_line(line, repeat=0):
    '''
    Function to translate a line from English to Spanish.
    :param line: The English Line
    :return: dict object of translation
    '''

    # Test for potential issues with translate service.
    # Do NOT attempt to translate more than 3 times.
    if repeat > 2: return False

    # The API used for translation
    translate_api = "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&lang={}&text={}".format(yandex_key, "en-es", line)

    # Try to submit request to Translation Service
    try:
        # Send request to API Server
        print("    Sending translation request.")
        r = requests.get(translate_api)
        # print(r.json())

        # Verify successful request to API Server, it not try again
        if r.status_code != 200:
            print("    There was a problem with the translation.  Trying again.")
            return translate_line(line, repeat=repeat + 1)
    except:
        # In case of error, try again 2 times
        print("    Couldn't reach translation service.  Trying again.")
        return translate_line(line, repeat=repeat+1)

    return r.json()

def send_line(line, number):
    '''
    Send the line via SMS Service
    :param line:
    :return:
    '''

    data = {
        "line": line,
        "number": number
    }

    r = requests.post(tropo_server, data=data)



class Score(Resource):
    '''
    API Resource for main service function.
     Receives a request and then:
      1. Translate the request
      2. Send Message via SMS
    '''
    def post(self):
        '''
        Process incoming request
        :return:
        '''
        # Process the incoming Arguments
        api_args = api_parser.parse_args()
        message = "Incoming Request: Line - '{}', Phone Number - {}".format(api_args["line"],
                                                                            api_args["phonenumber"])
        print(message)

        # Attempt to translate the line
        translation = translate_line(api_args["line"])
        message = "    Translation = '{}'".format(translation["text"][0])

        # In case of an error in translation
        if not translation:
            # Setup return data and status
            return_data = {
                "status": "error",
                "message": "Error in Translation."
            }
            return_status = 400
            message += "\n    Error with request: "

        # Print log message.
        print(message)

        # If translation AND phonenumber, attempt to SMS
        if translation and api_args["phonenumber"]:
            message = "    Sending SMS Message."
            send_line(translation["text"][0], api_args["phonenumber"])
            print(message)

        # Setup return data and status
        return_data = {
            "status": "success",
            "message": "success",
            "line": api_args["line"],
            "phonenumber": api_args["phonenumber"],
            "translation": translation["text"][0]
           }
        return_status = 200

        # Send results
        return json.dumps(return_data), return_status

# Add API Resource
api.add_resource(Score, "/api/score")

if __name__=='__main__':
    # Use ArgParse to retrieve command line parameters.
    from argparse import ArgumentParser
    parser = ArgumentParser("Haciendo API Server")

    # Retrieve the port and API server address
    parser.add_argument(
        "-p", "--port", help="Port to run API server on.", required=True
    )
    parser.add_argument(
        "-t", "--troposerver", help="Address of Tropo Server.", required=True
    )
    parser.add_argument(
        "-y", "--yandexkey", help="API Key for Yandex Service.", required=True
    )
    args = parser.parse_args()

    # Set the API Port Variable
    api_port = int(args.port)
    tropo_server = args.troposerver
    yandex_key = args.yandexkey


    # Start the server
    app.run(debug=True, host='0.0.0.0', port=api_port)
