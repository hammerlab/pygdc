import logging
import json
import pandas as pd
import requests

from .urls import GDC_API_URL

def _endpoint_url(endpoint):
    assert endpoint in set(['projects', 'files', 'cases'])
    return GDC_API_URL + '/' + endpoint

def _get_endpoint(endpoint, filters, fields, sort, start=1, max_results=None):
    logging.info("Making request to endpoint {}".format(endpoint))

    params = {'fields': fields, 'filters': filters, 'from': start, 'sort' : sort}
    if max_results:
        params['size'] = max_results

    response = requests.get(
                 url=_endpoint_url(endpoint),
                 params=params 
        )

    logging.info("Request returned with status code {}".format(response.status_code))
    if response.status_code != 200:
        raise ValueError(response.text)

    parsed_response = json.loads(response.text)['data']
    return parsed_response

def _get_endpoint_results(endpoint, filters, fields, sort, max_results=None):

    start = 1
    results_count = 0
    results = []
    while max_results is None or results_count < max_results:
        partial_results = _get_endpoint(endpoint, filters, fields, sort, start, max_results)

        pagination_info = partial_results['pagination']
        total = int(pagination_info['total'])
        if max_results is None or max_results > total:
            max_results = total
   
        partial_results_count = int(pagination_info['count'])
        start += partial_results_count
        results_count += partial_results_count
        results += partial_results['hits']

    logging.info("Result contains {} records".format(len(results)))

    return results


def get_cases(filters, fields='', max_results=None):
    results = _get_endpoint_results('cases', filters=filters, fields=fields, sort='case_id', max_results=max_results)
    return results

def get_projects(filters, fields=''):
    results = _get_endpoint_results('projects', filters=filters, fields=fields, sort='project_id',)
    return pd.DataFrame.from_dict(results)

def get_files(filters, fields='', max_results=None):
    results = _get_endpoint_results('files', filters=filters, fields=fields, sort='file_id', max_results=max_results)
    return results