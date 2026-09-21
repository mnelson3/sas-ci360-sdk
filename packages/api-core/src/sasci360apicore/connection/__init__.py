#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import time

import requests


class Connection:
    """
    Connection Module
    Contains operations to connect to REST APIs
            1. def connect(self, **kwargs) -> dict | int | bytes | None
    """

    # One request function per supported HTTP verb, keyed by the `action`
    # keyword. Kept as a dispatch table (rather than an if/elif chain) so
    # connect() doesn't grow a branch per verb.
    _ACTION_HANDLERS = {
        "DELETE": lambda url, data, headers, params: requests.delete(url=url, headers=headers),
        "GET": lambda url, data, headers, params: requests.get(url=url, params=params, headers=headers),
        "PATCH": lambda url, data, headers, params: requests.patch(url=url, data=data, headers=headers),
        "POST": lambda url, data, headers, params: requests.post(url=url, data=data, headers=headers),
        "PUT": lambda url, data, headers, params: requests.put(url=url, data=open(data, "rb"), headers=headers),
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def connect(self, **kwargs):
        """
        Connect
        :keywords action: str, required - method of operation to perform (DELETE, GET, PATCH, POST, PUT)
        :keywords data: dict, optional - package to be processed, valid with PATCH, POST, PUT actions
        :keywords headers: dict, required - an HTTP header that can be used in an HTTP
                request to provide information about the request context, so that the
                server can tailor the response
        :keywords params: str, optional - GET-style URL parameters, currently not implemented
        :keywords url: str, required - the web resource to access via HTTP(S) for the REST APIs
        :return: the parsed JSON body, or the response's raw bytes when the body isn't JSON, or
                the status code for a PUT (signed-URL uploads typically return an empty body)
        """
        result = None
        try:
            r = None
            action = kwargs.get("action")
            data = kwargs.get("data")
            headers = kwargs.get("headers")
            params = kwargs.get("params")
            url = kwargs.get("url")

            code = 500
            counter = 0
            while (not 200 <= code <= 299) and (counter < 3):
                time.sleep(3)
                handler = self._ACTION_HANDLERS.get(action)
                if handler is not None:
                    r = handler(url, data, headers, params)
                counter += 1
                code = int(r.status_code)
            if 200 <= code <= 299:
                if action == "PUT":
                    result = code
                else:
                    try:
                        result = r.json()
                    except ValueError:
                        result = r.content
            r.close()
        except (requests.exceptions.RequestException, OSError) as e:
            self.logger.exception("Exception occurred: {}".format(str(e)))
        except AttributeError as e:
            # r stays None when action doesn't match a handled HTTP verb.
            self.logger.exception("Exception occurred: {}".format(str(e)))
        return result


if __name__ == "__main__":
    Connection()
