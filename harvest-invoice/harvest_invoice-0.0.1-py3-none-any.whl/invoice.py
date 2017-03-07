# -*- coding: utf-8 -*-

import requests

BASE_URL = "https://kriwil.harvestapp.com"

CLIENTS_URL = "{}/clients".format(BASE_URL)
INVOICES_URL = "{}/invoices".format(BASE_URL)
PROJECTS_URL = "{}/projects".format(BASE_URL)

USER_AUTH = ("kriwil@gmail.com", "rGIkFhVMNT8GUohVlxty")


def generate():
    get_next_invoice_number()
    # project = get_project(code="KRWL")
    # print(project)


def get_list(url):
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    response = requests.get(url, auth=USER_AUTH, headers=headers)
    return response.json()


def get_clients():
    return get_list(CLIENTS_URL)


def get_invoices():
    return get_list(INVOICES_URL + "?page=1")


def get_projects():
    return get_list(PROJECTS_URL)


def get_latest_invoice_number():
    invoices = get_invoices()
    latest_invoice = invoices[0]
    return latest_invoice["invoices"]["number"]


def get_next_invoice_number():
    latest_number = get_latest_invoice_number()
    number = ''.join(ch for ch in latest_number if ch.isdigit())
    prefix = latest_number.replace(number, "")

    next_number = int(number) + 1
    next_invoice_number = "{}{}".format(prefix, str(next_number).zfill(len(number)))
    return next_invoice_number


def get_project(code):
    projects = get_projects()
    for project in projects:
        if project["project"]["code"] == code:
            return project["project"]
    return None
