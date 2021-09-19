import urllib.parse
import json

import requests

from requests_oauthlib import OAuth1
from requests.exceptions import TooManyRedirects, HTTPError


class TumblrRequest(object):
    """
    A simple request object that lets us query the Tumblr API
    """

    __version = "0.0.1"

    def __init__(
        self,
        consumer_key,
        consumer_secret="",
        oauth_token="",
        oauth_secret="",
        host="https://api.tumblr.com",
    ):
        self.host = host
        self.oauth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret,
        )
        self.consumer_key = consumer_key

        self.headers = {
            "User-Agent": "pytumblr2/" + self.__version,
        }

        self.last_response_headers = None

    def get(self, url, params):
        """
        Issues a GET request against the API, properly formatting the params

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the paramaters needed
                       in the request
        :returns: a dict parsed of the JSON response
        """
        url = self.host + url
        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        try:
            resp = requests.get(
                url, allow_redirects=False, headers=self.headers, auth=self.oauth
            )
        except TooManyRedirects as e:
            resp = e.response

        return self.json_parse(resp)

    def post(self, url, params={}, files=[]):
        """
        Issues a POST request against the API, allows for multipart data uploads

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the parameters needed
                       in the request
        :param files: a list, the list of tuples of files

        :returns: a dict parsed of the JSON response
        """
        url = self.host + url
        try:
            if files:
                return self.post_multipart(url, params, files)
            else:
                resp = requests.post(
                    url, json=params, headers=self.headers, auth=self.oauth
                )
                return self.json_parse(resp)
        except HTTPError as e:
            return self.json_parse(e.response)

    def put(self, url, params={}, files=[]):
        """
        Issues a PUT request against the API, allows for multipart data uploads

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the parameters needed
                       in the request
        :param files: a list, the list of tuples of files

        :returns: a dict parsed of the JSON response
        """
        url = self.host + url
        try:
            if files:
                return self.post_multipart(url, params, files)
            else:
                resp = requests.put(
                    url, json=params, headers=self.headers, auth=self.oauth
                )
                return self.json_parse(resp)
        except HTTPError as e:
            return self.json_parse(e.response)

    def delete(self, url, params):
        """
        Issues a DELETE request against the API, properly formatting the params

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the paramaters needed
                       in the request
        :returns: a dict parsed of the JSON response
        """
        url = self.host + url
        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        try:
            resp = requests.delete(
                url, allow_redirects=False, headers=self.headers, auth=self.oauth
            )
        except TooManyRedirects as e:
            resp = e.response

        return self.json_parse(resp)

    def json_parse(self, response):
        """
        Wraps and abstracts response validation and JSON parsing
        to make sure the user gets the correct response.

        :param response: The response returned to us from the request

        :returns: a dict of the json response
        """
        self.last_response_headers = response.headers

        try:
            data = response.json()
        except ValueError:
            data = {
                "meta": {"status": response.status_code, "msg": response.reason},
                "response": {
                    "error": "API response could not be JSON parsed. 'meta' field has been generated on the client side."
                },
            }

        # We only really care about the response if we succeed
        # and the error if we fail
        if 200 <= data["meta"]["status"] <= 399:
            return data["response"]
        else:
            return data

    def post_multipart(self, url, params, files):
        """
        Generates and issues a multipart request for data files

        :param url: a string, the url you are requesting
        :param params: a dict, a key-value of all the parameters
        :param files:  a dict, matching the form '{name: file descriptor}'

        :returns: a dict parsed from the JSON response
        """
        resp = requests.post(
            url,
            data=params,
            params=params,
            files=files,
            headers=self.headers,
            allow_redirects=False,
            auth=self.oauth,
        )
        return self.json_parse(resp)
