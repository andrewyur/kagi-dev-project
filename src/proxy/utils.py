import requests


def check_request(url):
    try:
        response = requests.get(url, headers={"user-agent": "andrew's rss converter"})
    except requests.exceptions.Timeout:
        return "Request timed out!"
    except requests.exceptions.TooManyRedirects:
        return "Too many redirects!"
    except requests.RequestException:
        return "Could not send http request!"

    if not response.ok:
        return "The server responded with an error code!"

    # this is only for the initial html page, not anything else
    if not response.headers["Content-Type"].startswith("text/html"):
        return "Expected an html response!"

    return response
