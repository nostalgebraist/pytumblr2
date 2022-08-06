import warnings

from .helpers import PostIdentifier, validate_blogname, simulate_legacy_payload
from .request import TumblrRequest


class TumblrRestClient(object):
    """
    A Python Client for the Tumblr API
    """

    def __init__(
        self,
        consumer_key,
        consumer_secret="",
        oauth_token="",
        oauth_secret="",
        host="https://api.tumblr.com",
        consume_in_npf_by_default=True,
        convert_npf_to_legacy_html=False,
    ):
        """
        Initializes the TumblrRestClient object, creating the TumblrRequest
        object which deals with all request formatting.

        :param consumer_key: a string, the consumer key of your
                             Tumblr Application
        :param consumer_secret: a string, the consumer secret of
                                your Tumblr Application
        :param oauth_token: a string, the user specific token, received
                            from the /access_token endpoint
        :param oauth_secret: a string, the user specific secret, received
                             from the /access_token endpoint
        :param host: the host that are you trying to send information to,
                     defaults to https://api.tumblr.com

        :returns: None
        """
        self.consume_in_npf_by_default = consume_in_npf_by_default
        self.convert_npf_to_legacy_html = convert_npf_to_legacy_html
        self.request = TumblrRequest(
            consumer_key, consumer_secret, oauth_token, oauth_secret, host
        )
        # TODO: is this actually useful?  (yes, in load balancer)
        # self.api_key_blogname = self._retrieve_api_key_blogname()

        self.reblog_requirements_cache = {}

    def npf_consumption_on(self):
        self.consume_in_npf_by_default = True

    def npf_consumption_off(self):
        self.consume_in_npf_by_default = False

    def legacy_conversion_on(self):
        self.convert_npf_to_legacy_html = True

    def legacy_conversion_off(self):
        self.convert_npf_to_legacy_html = False

    @staticmethod
    def is_consumption_endpoint(url: str) -> bool:
        return "/posts" in url or "/dashboard" in url

    def _retrieve_api_key_blogname(self):
        return self.info().get("user", {}).get("name")

    def info(self):
        """
        Gets the information about the current given user

        :returns: A dict created from the JSON response
        """
        return self.send_api_request("get", "/v2/user/info")

    @validate_blogname
    def avatar(self, blogname, size=64):
        """
        Retrieves the url of the blog's avatar

        :param blogname: a string, the blog you want the avatar for

        :returns: A dict created from the JSON response
        """
        url = "/v2/blog/{}/avatar/{}".format(blogname, size)
        return self.send_api_request("get", url)

    def likes(self, **kwargs):
        """
        Gets the current given user's likes
        :param limit: an int, the number of likes you want returned
        (DEPRECATED) :param offset: an int, the like you want to start at, for pagination.
        :param before: an int, the timestamp for likes you want before.
        :param after: an int, the timestamp for likes you want after.

            # Start at the 20th like and get 20 more likes.
            client.likes({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        return self.send_api_request("get", "/v2/user/likes", kwargs)

    def following(self, **kwargs):
        """
        Gets the blogs that the current user is following.
        :param limit: an int, the number of likes you want returned
        :param offset: an int, the blog you want to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.following({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        return self.send_api_request("get", "/v2/user/following", kwargs)

    def dashboard(self, **kwargs):
        """
        Gets the dashboard of the current user

        :param limit: an int, the number of posts you want returned
        :param offset: an int, the posts you want to start at, for pagination.
        :param type:   the type of post you want to return
        :param since_id:  return only posts that have appeared after this ID
        :param reblog_info: return reblog information about posts
        :param notes_info:  return notes information about the posts

        :returns: A dict created from the JSON response
        """
        return self.send_api_request("get", "/v2/user/dashboard", kwargs)

    def tagged(self, tag, **kwargs):
        """
        Gets a list of posts tagged with the given tag

        :param tag: a string, the tag you want to look for
        :param before: a unix timestamp, the timestamp you want to start at
                       to look at posts.
        :param limit: the number of results you want
        :param filter: the post format that you want returned: html, text, raw

            client.tagged("gif", limit=10)

        :returns: a dict created from the JSON response
        """
        kwargs.update({"tag": tag})
        return self.send_api_request("get", "/v2/tagged", kwargs, True)

    @validate_blogname
    def legacy_posts_by_type(self, blogname, type, **kwargs):
        """
        Gets a list of posts from a particular blog, filtered to a specific post type (legacy only)

        :param blogname: a string, the blogname you want to look up posts
                         for. eg: codingjester.tumblr.com
        :param type: a string, the type of post to include
        :param id: an int, the id of the post you are looking for on the blog
        :param tag: a string, the tag you are looking for on posts
        :param limit: an int, the number of results you want
        :param offset: an int, the offset of the posts you want to start at.
        :param before: an int, the timestamp for posts you want before.
        :param filter: the post format you want returned: HTML, text or raw.
        :param type: the type of posts you want returned, e.g. video. If omitted returns all post types.

        :returns: a dict created from the JSON response
        """

        url = "/v2/blog/{}/posts/{}".format(blogname, type)
        return self.send_api_request("get", url, kwargs, True)

    @validate_blogname
    def posts(self, blogname, **kwargs):
        """
        Gets a list of posts from a particular blog

        :param blogname: a string, the blogname you want to look up posts
                         for. eg: codingjester.tumblr.com
        :param id: an int, the id of the post you are looking for on the blog
        :param tag: a string, the tag you are looking for on posts
        :param limit: an int, the number of results you want
        :param offset: an int, the offset of the posts you want to start at.
        :param before: an int, the timestamp for posts you want before.
        :param filter: the post format you want returned: HTML, text or raw.
        :param type: the type of posts you want returned, e.g. video. If omitted returns all post types.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts".format(blogname)
        return self.send_api_request("get", url, kwargs, True)

    @validate_blogname
    def notifications(self, blogname, **kwargs):
        """
        Gets a list of activity notifications for a particular blog

        :param blogname: a string, the blogname you want to look up posts
                         for. eg: codingjester.tumblr.com
        :param before: an int, the timestamp for posts you want before.
        :param type: An array of one or more notification types to filter by, or none if you want all

        NOTE: the `type` parameter of the notifications endpoint has been historically unreliable.  If in doubt, don't use it.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/notifications".format(blogname)
        return self.send_api_request("get", url, kwargs, True)

    @validate_blogname
    def blog_info(self, blogname):
        """
        Gets the information of the given blog

        :param blogname: the name of the blog you want to information
                         on. eg: codingjester.tumblr.com

        :returns: a dict created from the JSON response of information
        """
        url = "/v2/blog/{}/info".format(blogname)
        return self.send_api_request("get", url, {}, True)

    @validate_blogname
    def blog_following(self, blogname, **kwargs):
        """
        Gets the publicly exposed list of blogs that a blog follows

        :param blogname: the name of the blog you want to get information on.
                         eg: codingjester.tumblr.com

        :param limit: an int, the number of blogs you want returned
        :param offset: an int, the blog to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.blog_following('pytblr', offset=20, limit=20})

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/following".format(blogname)
        return self.send_api_request("get", url, kwargs)

    @validate_blogname
    def followers(self, blogname, **kwargs):
        """
        Gets the followers of the given blog
        :param limit: an int, the number of followers you want returned
        :param offset: an int, the follower to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.followers({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        url = "/v2/blog/{}/followers".format(blogname)
        return self.send_api_request("get", url, kwargs)

    @validate_blogname
    def blog_likes(self, blogname, **kwargs):
        """
        Gets the current given user's likes
        :param limit: an int, the number of likes you want returned
        (DEPRECATED) :param offset: an int, the like you want to start at, for pagination.
        :param before: an int, the timestamp for likes you want before.
        :param after: an int, the timestamp for likes you want after.

            # Start at the 20th like and get 20 more likes.
            client.blog_likes({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        url = "/v2/blog/{}/likes".format(blogname)
        return self.send_api_request("get", url, kwargs, True)

    @validate_blogname
    def queue(self, blogname, **kwargs):
        """
        Gets posts that are currently in the blog's queue

        :param limit: an int, the number of posts you want returned
        :param offset: an int, the post you want to start at, for pagination.
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts/queue".format(blogname)
        return self.send_api_request("get", url, kwargs)

    @validate_blogname
    def drafts(self, blogname, **kwargs):
        """
        Gets posts that are currently in the blog's drafts
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts/draft".format(blogname)
        return self.send_api_request("get", url, kwargs)

    @validate_blogname
    def submission(self, blogname, **kwargs):
        """
        Gets posts that are currently in the blog's submission list

        :param offset: an int, the post you want to start at, for pagination.
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts/submission".format(blogname)
        return self.send_api_request("get", url, kwargs)

    @validate_blogname
    def follow(self, blogname):
        """
        Follow the url of the given blog

        :param blogname: a string, the blog url you want to follow

        :returns: a dict created from the JSON response
        """
        url = "/v2/user/follow"
        return self.send_api_request("post", url, {"url": blogname})

    @validate_blogname
    def unfollow(self, blogname):
        """
        Unfollow the url of the given blog

        :param blogname: a string, the blog url you want to follow

        :returns: a dict created from the JSON response
        """
        url = "/v2/user/unfollow"
        return self.send_api_request("post", url, {"url": blogname})

    def like(self, id, reblog_key):
        """
        Like the post of the given blog

        :param id: an int, the id of the post you want to like
        :param reblog_key: a string, the reblog key of the post

        :returns: a dict created from the JSON response
        """
        url = "/v2/user/like"
        params = {"id": id, "reblog_key": reblog_key}
        return self.send_api_request("post", url, params, ["id", "reblog_key"])

    def unlike(self, id, reblog_key):
        """
        Unlike the post of the given blog

        :param id: an int, the id of the post you want to like
        :param reblog_key: a string, the reblog key of the post

        :returns: a dict created from the JSON response
        """
        url = "/v2/user/unlike"
        params = {"id": id, "reblog_key": reblog_key}
        return self.send_api_request("post", url, params)

    @validate_blogname
    def create_post(self, blogname, **kwargs):
        """
        Create a new NPF post

        :param blogname: a string, the url of the blog you want to post to.
        :param content: list of NPF content blocks
        :param layout: list of NPF layout entries
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param date: a string, the GMT date and time of the post
        :param slug: a string, a short text summary to the end of the post url
        :param media_sources: a dict containing media to be uploaded, of the form {identifier: path_or_file_object}

        :returns: a dict created from the JSON response
        """
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def edit_post(self, blogname, id, **kwargs):
        """
        Edit an NPF post

        :param blogname: a string, the url of the blog you want to post to.
        :param id: an integer, the id of the post you want to edit.
        :param content: list of NPF content blocks
        :param layout: list of NPF layout entries
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param date: a string, the GMT date and time of the post
        :param slug: a string, a short text summary to the end of the post url
        :param media_sources: a dict containing media to be uploaded, of the form {identifier: path_or_file_object}

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts/{}".format(blogname, id)
        return self.send_api_request('put', url, kwargs)

    @validate_blogname
    def reblog_post(self, blogname, parent_blogname, id,
                    parent_blog_uuid=None,
                    reblog_key=None,
                    **kwargs):
        """
        Creates a reblog on the given blogname (legacy)

        :param blogname: a string, the url of the blog you want to reblog TO
        :param parent_blogname: a string, the name of the blog you want to reblog FROM
        :param id: an int, the post id that you are reblogging

        :param parent_blog_uuid: an optional string, the UUID of the blog you want to reblog FROM
        :param reblog_key: a optional string, the reblog key of the post that you are reblogging

        Note: to reblog a post in NPF, we need the following information:
            - the UUID (not just the name) of the blog we're reblogging from
            - the reblog key of the post we're reblogging

        These can only be obtained via a GET request on the post.

        This client caches this information when it does GET requests, so even if you don't know this information,
        it may already be in the cache.

        If it's not in the cache, we'll send a GET request to fetch it before we make the POST request to make the reblog.

        If reblog_key is not provided, this method may send a GET request to get the key.
        reblog keys are cached, so this will only happen once per post per client object.

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/posts/".format(blogname)

        if parent_blog_uuid and reblog_key:
            reblog_requirements = {
                "blog_uuid": parent_blog_uuid,
                "reblog_key": reblog_key
            }
        else:
            post_identifier = PostIdentifier(parent_blogname, id)
            reblog_requirements = self._get_reblog_requirements(post_identifier)

        kwargs.update(
            {
                "parent_tumblelog_uuid": reblog_requirements["blog_uuid"],
                "parent_post_id": id,
                "reblog_key": reblog_requirements["reblog_key"],

            }
        )

        if "tags" in kwargs and not isinstance(kwargs["tags"], str):
            # Take a list of tags and make them acceptable for upload
            kwargs["tags"] = ",".join(kwargs["tags"])
        return self.send_api_request("post", url, kwargs)

    def _get_reblog_requirements(self, post_identifier: PostIdentifier):
        if post_identifier not in self.reblog_requirements_cache:
            self.get_single_post(*post_identifier)  # populates cache
        return self.reblog_requirements_cache[post_identifier]

    @validate_blogname
    def legacy_create_photo(self, blogname, **kwargs):
        """
        Create a new legacy photo post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption that you want applied to the photo
        :param link: a string, the 'click-through' url you want on the photo
        :param source: a string, the photo source url
        :param data: a string or a list of the path of photo(s)

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "photo"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_text(self, blogname, **kwargs):
        """
        Create a new legacy text post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the optional title of a post
        :param body: a string, the body of the text post

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "text"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_quote(self, blogname, **kwargs):
        """
        Create a new legacy quote post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param quote: a string, the full text of the quote
        :param source: a string, the cited source of the quote

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "quote"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_link(self, blogname, **kwargs):
        """
        Create a new legacy link post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the title of the link
        :param url: a string, the url of the link you are posting
        :param description: a string, the description of the link you are posting

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "link"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_chat(self, blogname, **kwargs):
        """
        Create a new legacy chat post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the title of the conversation
        :param conversation: a string, the conversation you are posting

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "chat"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_audio(self, blogname, **kwargs):
        """
        Create a new legacy audio post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption for the post
        :param external_url: a string, the url of the audio you are uploading
        :param data: a string, the local filename path of the audio you are uploading

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "audio"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_create_video(self, blogname, **kwargs):
        """
        Create a new legacy video post

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption for the post
        :param embed: a string, the emebed code that you'd like to upload
        :param data: a string, the local filename path of the video you are uploading

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "video"})
        return self._send_post_legacy(blogname, kwargs)

    @validate_blogname
    def legacy_reblog(self, blogname, **kwargs):
        """
        Creates a reblog on the given blogname (legacy)

        :param blogname: a string, the url of the blog you want to reblog to
        :param id: an int, the post id that you are reblogging
        :param reblog_key: a string, the reblog key of the post
        :param comment: a string, a comment added to the reblogged post

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/post/reblog".format(blogname)

        if "tags" in kwargs and not isinstance(kwargs["tags"], str):
            # Take a list of tags and make them acceptable for upload
            kwargs["tags"] = ",".join(kwargs["tags"])
        return self.send_api_request("post", url, kwargs)

    @validate_blogname
    def delete_post(self, blogname, id):
        """
        Deletes a post with the given id

        :param blogname: a string, the url of the blog you want to delete from
        :param id: an int, the post id that you want to delete

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/post/delete".format(blogname)
        return self.send_api_request("post", url, {"id": id})

    @validate_blogname
    def legacy_edit_post(self, blogname, id, **kwargs):
        """
        Edits a post with a given id (legacy)

        :param blogname: a string, the url of the blog you want to edit
        :param state: a string, the state of the post. published, draft, queue, or private.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param id: an int, the post id that you want to edit

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/post/edit".format(blogname)

        kwargs.update({"id": id})

        if "tags" in kwargs and not isinstance(kwargs["tags"], str):
            # Take a list of tags and make them acceptable for upload
            kwargs["tags"] = ",".join(kwargs["tags"])

        return self.send_api_request("post", url, kwargs)

    @validate_blogname
    def notes(self, blogname, id, **kwargs):
        """
        Gets the notes

        :param blogname: a string, the url of the blog that houses the post
        :param id: a string, the id of the post.
        :param mode: a string. Undocumented. Automatically added by tumblr but it's use is not yet known.
        :param before_timestamp: a string, retreives data before this timestamp

        :returns: a dict created from the JSON response
        """
        url = "/v2/blog/{}/notes".format(blogname)
        kwargs.update({"id": id})
        return self.send_api_request("get", url, kwargs)

    def _send_post(self, blogname, params, npf=True):
        """
        Formats parameters and sends the API request off. Validates
        common and per-post-type parameters and formats your tags for you.

        :param blogname: a string, the blogname of the blog you are posting to
        :param params: a dict, the key-value of the parameters for the api request

        :returns: a dict parsed from the JSON response
        """
        if npf:
            url = "/v2/blog/{}/posts".format(blogname)
        else:
            url = "/v2/blog/{}/post".format(blogname)

        if len(params.get("tags", [])) > 0:
            # Take a list of tags and make them acceptable for upload
            params["tags"] = ",".join(params["tags"])

        return self.send_api_request("post", url, params)

    def _send_post_legacy(self, blogname, params):
        return self._send_post(blogname, params, npf=False)

    def send_api_request(self, method, url, params={}, needs_api_key=False):
        """
        Sends the url with parameters to the requested url, validating them
        to make sure that they are what we expect to have passed to us

        :param method: a string, the request method you want to make
        :param params: a dict, the parameters used for the API request
        :param needs_api_key: a boolean, whether or not your request needs an api key injected

        :returns: a dict parsed from the JSON response
        """
        if TumblrRestClient.is_consumption_endpoint(url) and method == "get":
            if "npf" not in params:
                params["npf"] = self.consume_in_npf_by_default

        if needs_api_key:
            params.update({"api_key": self.request.consumer_key})

        files = {}
        if "data" in params:
            # media uploads for legacy photo/video/etc post types
            if isinstance(params["data"], list):
                for idx, data in enumerate(params["data"]):
                    files["data[" + str(idx) + "]"] = open(params["data"][idx], "rb")
            else:
                files = {"data": open(params["data"], "rb")}
            del params["data"]


        if "media_sources" in params:
            # media uploads for NPF media blocks
            ks = list(params["media_sources"].keys())
            for k in ks:
                if isinstance(k, str):
                    # got file path, need file object
                    params["media_sources"][k] = open(params["media_sources"][k], "rb")

        if method == "get":
            response = self.request.get(url, params)
        elif method == "delete":
            response = self.request.delete(url, params)
        elif method == "put":
            response = self.request.put(url, params)
        else:
            response = self.request.post(url, params, files)

        if self.convert_npf_to_legacy_html and "posts" in response:
            response["posts"] = [simulate_legacy_payload(p) for p in response["posts"]]

        for post_payload in response.get("posts", []):
            post_identifier = PostIdentifier(post_payload["blog"]["name"], post_payload["id"])
            self.reblog_requirements_cache[post_identifier] = {
                "reblog_key": post_payload["reblog_key"],
                "blog_uuid": post_payload["blog"]["uuid"]
            }

        return response

    def get_single_post(self, blogname: str, id: int):
        """
        Wrapper around self.posts() to help retrieve single posts from the /posts endpoint.

        Returns the first (and only) entry of the 'posts' field in the API response.
        """
        response = self.posts(blogname, id=id)
        try:
            return response["posts"][0]
        except KeyError:
            # this happens if the call failed, e.g. if the blog name doesn't exist
            return response

    def get_ratelimit_data(self):
        if self.request.last_response_headers is None:
            warnings.warn("no ratelimit data found, sending a request to get it")
            self.dashboard()

        headers = self.request.last_response_headers
        results = {}

        results["day"] = {
            "remaining": int(headers["X-Ratelimit-Perday-Remaining"]),
            "reset": int(headers["X-Ratelimit-Perday-Reset"]),
        }

        results["hour"] = {
            "remaining": int(headers["X-Ratelimit-Perhour-Remaining"]),
            "reset": int(headers["X-Ratelimit-Perhour-Reset"]),
        }

        for k in ["day", "hour"]:
            results[k]["max_rate"] = results[k]["remaining"] / results[k]["reset"]

        results["effective_max_rate"] = min(
            [results[k]["max_rate"] for k in ["day", "hour"]]
        )
        results["effective_remaining"] = min(
            [results[k]["remaining"] for k in ["day", "hour"]]
        )
        results["effective_reset"] = min([results[k]["reset"] for k in ["day", "hour"]])

        return results
