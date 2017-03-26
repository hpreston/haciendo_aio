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

This is the web server element of the application.  Written in
Python and leveraging Flask and Jinja templates to present a
basic web interface for users to work with.
"""


from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    '''
    Serve the main web interface for Haciendo
    :return:
    '''
    return render_template("home.html")

@app.route("/", methods=['POST'])
def submit():
    '''
    Process a Submitted Line.
    Retrieve the information submitted and send to API server.
    Display the results back to the user.
    :return:
    '''
    msg = "Incoming Request: "      # Request Logging
    translated_line = None          # Placeholder for translation
    API_DOWN = False                # Placeholder for testing

    # Attempt to receive data from submission
    try:
        line = request.form["line"]         # Line submitted
        msg += "Line: {} ".format(line)

        # Look for Phone Number
        try:
            phonenumber = request.form["phonenumber"]       # Phone Number
            msg += "Phone Number: {} ".format(phonenumber)
        except KeyError:        # No phone number submitted
            phonenumber = None
            msg += "Note: No Phone Number"
            pass

        # Build data to submit to API Server
        submit_data = {
            "line": line,
            "phonenumber": phonenumber
        }

        # Try to submit request to API Server
        try:
            # Send request to API Server
            r = requests.post(api_server, json=submit_data)
            # Verify successful request to API Server
            if r.status_code == 201:
                msg += "\nData: {} ".format(r.json())
                translated_line = json.loads(r.json())["translation"]
            else:
                msg += "Error: There was a problem with the API Call\n"
                msg += "   Status Code: {} \n".format(r.status_code)
                msg += "   Headers: {} \n".format(r.headers)
                msg += "   Data: {} \n\n".format(r.text)
        except:
            msg += "\nError: API Server Not Available"
            API_DOWN = True

    except KeyError:        # No Line submitted
        msg += "Error: Line Missing."
        pass

    # Print log details
    print(msg)

    # Present web page to user
    return render_template("home.html",
                           translated_line=translated_line,
                           original_line=line,
                           phonenumber=phonenumber,
                           API_DOWN=API_DOWN
                           )

if __name__=='__main__':
    # Use ArgParse to retrieve command line parameters.
    from argparse import ArgumentParser
    parser = ArgumentParser("Haciendo Web Server")

    # Retrieve the port and API server address
    parser.add_argument(
        "-p", "--port", help="Port to run web server on.", required=True
    )
    parser.add_argument(
        "-a", "--apiserver", help="Address of API Server.", required=True
    )
    args = parser.parse_args()

    web_port = int(args.port)
    api_server = args.apiserver

    # Startup Logging Message
    print("Haciendo API Server: {} ".format(api_server))

    # Start the web server
    app.run(debug=True, host='0.0.0.0', port=web_port)
