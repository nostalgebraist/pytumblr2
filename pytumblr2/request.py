import urllib.parse
import json

import requests

from requests_oauthlib import OAuth1
from requests.exceptions import TooManyRedirects, HTTPError


class TumblrRequest(object):
    """
    A simple request object that lets us query the Tumblr API
    """

    __version = "0.2.2"

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
                return self.post_multipart_legacy(url, params, files)
            elif params.get('media_sources') is not None:
                real_params = {k: v for k, v in params.items() if k != 'media_sources'}
                media_sources = params['media_sources']
                return self.post_multipart_npf(url, real_params, media_sources)
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
                return self.put_multipart_legacy(url, params, files)
            elif params.get('media_sources') is not None:
                real_params = {k: v for k, v in params.items() if k != 'media_sources'}
                media_sources = params['media_sources']
                return self.put_multipart_npf(url, real_params, media_sources)
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

    def post_multipart_legacy(self, url, params, files):
        return self._send_multipart_legacy('post', url, params, files)

    def put_multipart_legacy(self, url, params, files):
        return self._send_multipart_legacy('put', url, params, files)

    def _send_multipart_legacy(self, method, url, params, files):
        """
        Generates and issues a multipart request for data files (legacy media posts)

        :param url: a string, the url you are requesting
        :param params: a dict, a key-value of all the parameters
        :param files:  a dict, matching the form '{name: file descriptor}'

        :returns: a dict parsed from the JSON response
        """
        resp = getattr(requests, method)(
            url,
            data=params,
            params=params,
            files=files,
            headers=self.headers,
            allow_redirects=False,
            auth=self.oauth,
        )
        return self.json_parse(resp)

    def post_multipart_npf(self, url, params, media_sources):
        return self._send_multipart_npf('post', url, params, media_sources)

    def put_multipart_npf(self, url, params, media_sources):
        return self._send_multipart_npf('put', url, params, media_sources)

    def _send_multipart_npf(self, method, url, params, media_sources):
        """
        Generates and issues a multipart request for data files (NPF media blocks)

        :param url: a string, the url you are requesting
        :param params: a dict, a key-value of all the parameters
        :param files:  a dict, matching the form '{name: file descriptor}'

        :returns: a dict parsed from the JSON response
        """

        # approach to multipart json + file requests taken from https://stackoverflow.com/a/35946962
        files = [
            ('json', (None, json.dumps(params), 'application/json')),
            *[
                (identifier, (str(i), media_sources[identifier]))
                for i, identifier in enumerate(media_sources.keys())
            ]
        ]

        resp = getattr(requests, method)(
            url,
            files=files,
            headers=self.headers,
            allow_redirects=False,
            auth=self.oauth,
        )
        return self.json_parse(resp)
