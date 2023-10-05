from googleapiclient.errors import HttpError

def call(f: Callable):
    return http.request(f.execute)

def request(f: Callable):
    try:
        return f()
    except HttpError as e:
        handle_response_status(e)

def handle_response_status(e: HttpError):
    if e.resp.status == 404:
        return None
    raise

