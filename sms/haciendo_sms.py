#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

This is the sms server element of the application.  Written in
Python and leveraging Flask and FlaskRestful it provides a basic
REST API to retrieve job requests and process them.  It leverages
other APIs including:

    - Translation Services from http://www.transltr.org
    - SMS Messaging Services from Tropo via the haciendo_sms service
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import requests, json, re
from requests.auth import HTTPBasicAuth
from itty import *
from tropo import Tropo, Session

tropo_host = "https://api.tropo.com/v1"
tropo_headers = {}
tropo_headers["Content-type"] = "application/json"

# ToDo - Convert to Flask from Itty... or find alternative for Python 3.5
# Unicode errors in P2.7
# itty doesn't support P3.5
#






# ITTY Versions
# @app.route('/', methods=["POST"])
@post('/')
def index(request):
    t = Tropo()

    # s = Session(request.get_json(force=True))
    sys.stderr.write(to_unicode(request.body) + "\n")

    s = Session(request.body)
    message = s.initialText
    # print("Initial Text: " + initialText)

    # Check if message contains word "results" and if so send results
    if not message:
        number = s.parameters["numberToDial"]
        reply = s.parameters["line"]
        t.call(to=number, network="SMS")

    else:
        reply = ["You have reached the Haciendo demo application.  " ]

    t.say(reply)
    response = t.RenderJson()
    sys.stderr.write(response + "\n")
    return response


@post('/score')
def send_line(request):
    number = request.POST.get("number", "Not found.")
    line = to_unicode(request.POST.get("line", "Not found."))
    sys.stderr.write("Sending line to: " + number + "\n")

    print(line)
    api_call = u"/sessions?action=create&token=%s&numberToDial=%s&line=%s" % (demoappmessagetoken, number, line)
    # api_call = u"/sessions?action=create&token={}&numberToDial={}&line={}".format(demoappmessagetoken, number, )
    u = u'' + tropo_host + api_call
    page = requests.get(u, headers=tropo_headers)
    print(u"API Call:" + u)


    # ToDo - For some reason the returned page isn't decoding properly.  Not needed to work, fix later
    # result= page.json()
    # sys.stderr.write(json.dumps(result) + "\n")

    headers = [
        ('Access-Control-Allow-Origin', '*')
    ]
    response = Response('Message sent to ' + number, headers=headers)
    return response


# Tropo API Details
@get('/application')
def display_tropo_application(request):

    return json.dumps(demoapp)

@get('/application/number')
def display_tropo_application_number(request):

    addresses = get_application_addresses(demoapp)
    numbers = []
    for address in addresses:
        if address["type"] == "number":
            numbers.append(address["number"])
    return json.dumps(numbers)
    # return json.dumps(demoappnumber)

@get('/hello/(?P<number>\w+)')
def send_hello(request, number):
    sys.stderr.write("Sending hello to: " + number + "\n")
    message = "Hello World!"

    u = tropo_host + "/sessions?action=create&token=%s&numberToDial=%s&line=%s" % (demoappmessagetoken, number, message)
    page = requests.get(u, headers=tropo_headers)
    # ToDo - For some reason the returned page isn't decoding properly.  Not needed to work, fix later
    # result= page.json()
    # sys.stderr.write(json.dumps(result) + "\n")

    headers = [
        ('Access-Control-Allow-Origin', '*')
    ]
    response = Response('Message sent to ' + number, headers=headers)
    return response

@get('/health')
def health_check(request):
    headers = [
        ('Access-Control-Allow-Origin', '*')
    ]
    response = Response('Service Up.', headers=headers)
    return response














# Tropo Utilities
def get_applications():
    tropo_u = tropo_host + "/applications"
    page = requests.get(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    applications = page.json()
    return applications

def get_application_addresses(application):
    tropo_u = tropo_host + "/applications/%s/addresses" % (application["id"])
    page = requests.get(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    addresses = page.json()
    return addresses

def create_application(appname, appurl):
    data = {
    "name":appname,
    "voiceUrl":appurl,
    "messagingUrl":appurl,
    "platform":"webapi",
    "partition":"staging"
    }

    tropo_u = tropo_host + "/applications"
    page = requests.post(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass), json=data)
    appurl = page.json()["href"]

    page = requests.get(appurl, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    app = page.json()
    return app

def set_application_url(application, appurl):
    data = {
    "name":application["name"],
    "voiceUrl":appurl,
    "messagingUrl":appurl,
    "platform":"webapi",
    "partition":"staging"
    }

    tropo_u = tropo_host + "/applications/%s" % (application["id"])
    page = requests.put(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass), json=data)
    appurl = page.json()["href"]

    page = requests.get(appurl, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    app = page.json()
    return app

def add_number(application, prefix):
    data = {
    "type":"number",
    "prefix":prefix
    }

    tropo_u = tropo_host + "/applications/%s/addresses" % (application["id"])
    page = requests.post(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass), json=data)
    if page.status_code == 200:
        # Success
        # print page
        addressurl = page.json()["href"]
        page = requests.get(addressurl, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
        address = page.json()
        return address
    else:
        return "Error: Failed to add number to application"

def add_token(application, type="messaging"):
    data = {
    "type":"token",
    "channel": type
    }

    tropo_u = tropo_host + "/applications/%s/addresses" % (application["id"])
    page = requests.post(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass), json=data)

    # {"href":"https://api.tropo.com/v1/applications/123456/addresses/token/12345679f90bac47a05b178c37d3c68aaf38d5bdbc5aba0c7abb12345d8a9fd13f1234c1234567dbe2c6f63b"}
    if page.status_code == 200:
        # Success
        # print page
        addressurl = page.json()["href"]
        page = requests.get(addressurl, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
        address = page.json()
        return address
    else:
        return "Error: Failed to add number to application"

def get_exchanges():
    # Example Exchange
    # {u'amountNumbersToOrder': 25,
    #  u'areaCode': u'443',
    #  u'city': u'Aberdeen',
    #  u'country': u'United States',
    #  u'countryDialingCode': u'1',
    #  u'description': u'',
    #  u'href': u'https://api.tropo.com/rest/v1/exchanges/2142',
    #  u'id': 2142,
    #  u'minNumbersInExchange': 10,
    #  u'prefix': u'1443',
    #  u'requiresVerification': False,
    #  u'state': u'MD',
    #  u'tollFree': False}
    tropo_u = tropo_host + "/exchanges"
    page = requests.get(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    exchanges = page.json()
    return exchanges

def get_available_numbers(exchange):
    # Example Exchange
    #  {u'city': u'Aberdeen',
    # u'country': u'United States',
    # u'displayNumber': u'+1 443-863-7082',
    # u'href': u'https://api.tropo.com/rest/v1/addresses/number/+14438637082',
    # u'number': u'+14438637082',
    # u'prefix': u'1443',
    # u'smsEnabled': True,
    # u'state': u'MD',
    # u'subscriber': False,
    # u'type': u'number'}
    tropo_u = tropo_host + "/addresses?available=true&type=NUMBER&prefix=%s" % (exchange)
    page = requests.get(tropo_u, headers = tropo_headers, auth=HTTPBasicAuth(tropo_user, tropo_pass))
    numbers = page.json()
    sms_numbers = []
    for number in numbers:
        if number["smsEnabled"]:
            sms_numbers.append(number)
    return sms_numbers

def test_exchange(exchange):
    exchanges = get_available_numbers(exchange)
    if len(exchanges) > 0:
        return True
    else:
        return False



if __name__ == '__main__':
    from argparse import ArgumentParser
    import os, sys
    from pprint import pprint

    # Setup and parse command line arguments
    parser = ArgumentParser("Haciendo SMS Application - Tropo")
    parser.add_argument(
        "-p", "--port", help="Port to run SMS server on.", required=True
    )
    parser.add_argument(
        "-t", "--tropouser", help="Tropo Username", required=True
    )
    parser.add_argument(
        "-w", "--tropopass", help="Tropo Password", required=True
    )
    parser.add_argument(
        "--tropoprefix", help="Tropo Number Prefix", required=True
    )
    parser.add_argument(
        "--tropourl", help="Local Address for Tropo App URL", required=True
    )

    args = parser.parse_args()

    # Set the SMS Port Variable
    sms_port = int(args.port)


    tropo_user = args.tropouser
    sys.stderr.write("Tropo User: " + tropo_user + "\n")

    tropo_prefix = args.tropoprefix
    sys.stderr.write("Tropo Prefix: " + tropo_prefix + "\n")

    tropo_pass = args.tropopass
    sys.stderr.write("Tropo Pass: REDACTED\n")

    tropo_url = args.tropourl
    sys.stderr.write("Tropo URL: " + tropo_url + "\n")


    # Find if Tropo Application "haciendo" already exists
    # If not, create it
    # If exists, verify has correct url and a number in the correct prefix
    tropo_applications = get_applications()

    demoappname = "haciendo " + tropo_url[len("http://"):tropo_url.find("-tropo")+len("-tropo")]
    demoappid = ""
    demoapp = {}
    demoappnumbers = []
    demoappnumber = ""
    demoappprefix = ""
    demoappmessagetoken = ""

    for app in tropo_applications:
        if app["name"] == demoappname:
            # pprint("Found Demo App")
            demoappid = app["id"]
            demoapp = app
            if demoapp["messagingUrl"] != tropo_url:
                pprint("Updated App URLs")
                demoapp = set_application_url(demoapp, tropo_url)

    if demoappid == "":
        pprint("Creating Tropo App")
        demoapp = create_application(demoappname, tropo_url)
        demoappid = demoapp["id"]
        # pprint(demoapp)

    pprint("Tropo App: %s - %s" % (demoappid, demoapp["name"]))
    # pprint(demoapp)

    addresses = get_application_addresses(demoapp)
    for address in addresses:
        if address["type"] == "number":
            demoappnumbers.append(address["number"])
            if address["prefix"] == tropo_prefix:
                # pprint("Found Address")
                demoappnumber = address["number"]
                demoappprefix = address["prefix"]
        if address["type"] == "token" and address["channel"] == "messaging":
            demoappmessagetoken = address["token"]

    if demoappmessagetoken == "":
        pprint("Creating a Token")
        token = add_token(demoapp)
        demoappmessagetoken = token["token"]
        pprint("Token is: " + demoappmessagetoken)

    if demoappnumber == "":
        if test_exchange(tropo_prefix):
            pprint ("Creating Tropo Number")
            address = add_number(demoapp, tropo_prefix)
            demoappnumber = address["number"]
            demoappprefix = address["prefix"]
            demoappnumbers.append(demoappnumber)
        else:
            sys.stderr.write("Error: No numbers available for prefix %s.\n" % (tropo_prefix))

    sys.stderr.write("Tropo Number: " + ", ".join(demoappnumbers) + "\n")



    # Old itty commands
    # Only run if there is a number available
    if len(demoappnumbers) > 0:
        run_itty(server='wsgiref', host='0.0.0.0', port=sms_port)
    else:
        sys.stderr.write("Can't start Tropo Service, no numbers deployed to application.\n")
