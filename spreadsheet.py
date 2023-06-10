import os

from googleapiclient.errors import HttpError
import pandas as pd
import numpy as np

import google_api


def service():
    return google_api.service('sheets', 4)


def get_values(spreadsheet_id, range_names):
    # creds, _ = google.auth.default()
    # pylint: disable=maybe-no-member
    try:
        values = service().spreadsheets().values()
        def get_range(get_func): return get_func(
            spreadsheetId=spreadsheet_id, range=range_names,
            valueRenderOption='UNFORMATTED_VALUE').execute()
        if isinstance(range_names, str):
            return get_range(values.get)
        elif isinstance(range_names, list):
            return get_range(values.getBatch)
        else:
            raise Error("'range_names' should be of type str or list")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def get_spreadsheet() -> pd.DataFrame:
    # Pass: spreadsheet_id, and range_name
    tables = get_values(SPREADSHEET_ID, 'Sheet1')
    if 'values' in tables.keys():
        spreadsheet = pd.concat(map(pd.Series, tables['values']), axis=1)
    elif 'valueRanges' in tables.keys():
        valueRanges = tables['valueRanges']
        ranges = []
        for valueRange in valueRanges:
            values = valueRange['values']
            range = pd.concat(map(pd.Series, values), axis=1)
            ranges.append(range)
        spreadsheet = pd.concatenate(map(pd.Series, ranges), axis=1)
    else:
        raise Exception("The key 'range' or 'valueRanges' isn't found")
    spreadsheet[spreadsheet == '#N/A (No matches are found in FILTER evaluation.)'] = np.nan
    return spreadsheet


def create_value_range(range, values):
    return {
        'range': range,
        'majorDimension': 'COLUMNS',
        'values': values
    }


def update_values(spreadsheet_id, range_names, value_input_option,
                  values):
    # pylint: disable=maybe-no-member
    try:
        body = {
            'values': values
        }
        result = service().spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def batch_update_values(spreadsheet_id,
                        value_input_option, data):
    # pylint: disable=maybe-no-member
    try:
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }
        result = service().spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()
        print(f"{(result.get('totalUpdatedCells'))} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

