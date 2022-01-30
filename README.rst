PyTumblr2
=========
|Build Status|

A fork of `pytumblr <https://github.com/tumblr/pytumblr>`_, updated for the New Post Format era.

Quick demo, if you're familiar with pytumblr:

.. code:: python

    client = pytumblr2.TumblrRestClient(*keys)

    posts = client.posts('nostalgebraist')['posts']
    # by default, post content is fetched in NPF
    posts[0]['blocks']

    # fetch single posts easily
    post = client.get_single_post('nostalgebraist', 642337957436588032)

    client.legacy_conversion_on()
    post = client.get_single_post('nostalgebraist', 642337957436588032)
    # post content was fetched in NPF, then converted to legacy HTML and populated to 'body'
    post['body']

    # returns ratelimit info, from the headers of the most recent API response
    client.get_ratelimit_data()

    # if you're nostalgic for 2015
    client.npf_consumption_off()
    post = client.get_single_post('nostalgebraist', 642337957436588032)
    # post content was fetched in legacy
    post['body']

    # create post in NPF
    response = client.create_post(
        'your_blogname',
        content=[{'type': 'text', 'text': "I'm a bot using the beta editor!"}]
    )

    # reblog the post you just made, in NPF
    # no need for reblog keys / UUIDs
    # the client will fetch them if needed (with caching)
    client.reblog_post(
        'your_blogname',  # reblogging TO
        'your_blogname',  # rebloggin FROM
        response["id"],
        content=[{'type': 'text', 'text': "I'm reblogging myself"}]
    )

    # fetch notifications (the items that appear on the activity page)
    response = client.notifications('your_blogname')

Planned features that aren't implemented yet:
        - helpers for pagination
        - helpers for load balancing across clients

Installation
============

Install via pip:

.. code-block:: bash

    $ pip install pytumblr2

Install from source:

.. code-block:: bash

    $ git clone https://github.com/tumblr/pytumblr2.git
    $ cd pytumblr2
    $ python setup.py install

Usage
=====

Create a client
---------------

A ``pytumblr2.TumblrRestClient`` is the object you'll make all of your calls to the Tumblr API through. Creating one is this easy:

.. code:: python

    client = pytumblr2.TumblrRestClient(
        '<consumer_key>',
        '<consumer_secret>',
        '<oauth_token>',
        '<oauth_secret>',
    )

    client.info() # Grabs the current user information

Two easy ways to get your credentials to are:

1. The built-in ``interactive_console.py`` tool (if you already have a consumer key & secret)
2. The Tumblr API console at https://api.tumblr.com/console
3. Get sample login code at https://api.tumblr.com/console/calls/user/info

Consuming posts in NPF and legacy
---------------------------------

By default, methods that fetch posts will fetch them in NPF.

To control this, use

.. code:: python

    # after client construction
    client.npf_consumption_off()  # use legacy consumption, i.e. npf=false param in the API
    client.npf_consumption_on()  # use NPF consumption, i.e. npf=true param in the API

    # during client construction
    client = pytumblr2.TumblrRestClient(..., consume_in_npf_by_default=False)  # legacy consumption
    client = pytumblr2.TumblrRestClient(..., consume_in_npf_by_default=True)  # NPF consumption

Note that NPF consumption is `strongly recommended by the developers of tumblr <https://github.com/tumblr/docs/blob/master/api.md#response-12>`_.

Using PyTumblr2's native NPF-to-HTML conversation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer parsing HTML to parsing NPF, PyTumblr2 supports two ways of fetching posts in HTML/legacy format.

First, you can turn NPF consumption off, as described above.  When you fetch a post that was created in NPF, this will use tumblr's internal NPF-to-legacy conversion to produce a legacy response.

Second, you can use PyTumblr2's own NPF-to-legacy converter.  To do this:

.. code:: python

    # after client construction
    client.npf_consumption_on()
    client.legacy_conversion_on()

    # during client construction
    client = pytumblr2.TumblrRestClient(..., consume_in_npf_by_default=True, convert_npf_to_legacy_html=True)

A client in this state will return "hybrid" responses, containing fields from both NPF and legacy payloads:

- The response will contain NPF fields like ``content``. These come directly from the tumblr API response.
- The response will also contain legacy fields like ``body``. These were generated from the API response by PyTumblr2's converter.

Differences between PyTumblr2's converter and tumblr's:

- It behaves better in some cases where tumblr's converter fails, generally involving blockquotes. `Example <https://github.com/tumblr/docs/issues/36>`_
- It is not fully featured, and focused on text and image content. For example, it simply ignores videos.

Supported Methods
-----------------

User Methods
~~~~~~~~~~~~

.. code:: python

    client.info() # get information about the authenticating user
    client.dashboard() # get the dashboard for the authenticating user
    client.likes() # get the likes for the authenticating user
    client.following() # get the blogs followed by the authenticating user

    client.follow('codingjester.tumblr.com') # follow a blog
    client.unfollow('codingjester.tumblr.com') # unfollow a blog

    client.like(id, reblogkey) # like a post
    client.unlike(id, reblogkey) # unlike a post

Blog Methods
~~~~~~~~~~~~

.. code:: python

    client.blog_info(blogName) # get information about a blog
    client.posts(blogName, **params) # get posts for a blog
    client.get_single_post(blogName, id , **params) # get a single post
    client.avatar(blogName) # get the avatar for a blog
    client.blog_likes(blogName) # get the likes on a blog
    client.followers(blogName) # get the followers of a blog
    client.blog_following(blogName) # get the publicly exposed blogs that [blogName] follows
    client.queue(blogName) # get the queue for a given blog
    client.submission(blogName) # get the submissions for a given blog

Post creation and editing
-----------------------------

General note on using these methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Post creation and editing methods take a variety of keyword arguments.  Outside of a few special cases, these arguments are passed on directly to the tumblr API as key-value pairs in the json payload.

For example, the API spec `says <https://github.com/tumblr/docs/blob/master/api.md#request-parameters-24>`_  says ``content`` is a required field when creating an NPF post.  In PyTumblr2, you'll provide the value of this field by passing an argument ``content=[...]`` to the method ``create_post``.

For guidance on constructing these requests, you should consult

- `The tumblr API spec <https://github.com/tumblr/docs/blob/master/api.md>`_
    - for the names and meanings of the JSON fields that the API accepts in each type of request (e.g. "create NPF post," "edit legacy post")

- `The NPF spec <https://github.com/tumblr/docs/blob/master/npf-spec.md>`_
    - for information about how to compose posts in NPF using the ``content`` and (optionally) ``layout`` JSON fields


Creating posts
~~~~~~~~~~~~~~

Create posts in NPF with ``create_post``:

.. code:: python

    client.create_post(blogName, content=[{'type': 'text', 'text': "my post"}])

To create an NPF post containing media, pass an additional argument ``media_sources``.  The value should be a dict mapping each identifiers from the post's media blocks to a file path or file object.

.. code:: python

    client.create_post(
        blogName,
        content=[
            {"type": "text", 'text': "cool picture"},
            {"type": "image", "media": [{"type": "image/jpeg", "identifier": "my_media_identifier"}]}},
        ],
        media_sources={"my_media_identifier": "/Users/johnb/path/to/my/image.jpg"}
    )

If you want to create a legacy post, use one of the methods with a ``legacy_create_`` prefix.  For example:

.. code:: python

    #Creating a text post
    client.legacy_create_text(blogName, state="published", slug="testing-text-posts", title="Testing", body="testing1 2 3 4")

    #Creates a photo post using a source URL
    client.legacy_create_photo(blogName, state="published", tags=["testing", "ok"],
                               source="https://68.media.tumblr.com/b965fbb2e501610a29d80ffb6fb3e1ad/tumblr_n55vdeTse11rn1906o1_500.jpg")

    #Creates a photo post using a local filepath
    client.legacy_create_photo(blogName, state="queue", tags=["testing", "ok"],
                               tweet="Woah this is an incredible sweet post [URL]",
                               data="/Users/johnb/path/to/my/image.jpg")

    #Creates a photoset post using several local filepaths
    client.legacy_create_photo(blogName, state="draft", tags=["jb is cool"], format="markdown",
                               data=["/Users/johnb/path/to/my/image.jpg", "/Users/johnb/Pictures/kittens.jpg"],
                               caption="## Mega sweet kittens")

Editing a post
~~~~~~~~~~~~~~

Edit in NPF:

.. code:: python

    client.edit_post(blogName, post_id, content=[{'type': 'text', 'text': "edited"}])

Edit in legacy:

.. code:: python

    client.legacy_edit_post(blogName, id=post_id, type="photo", data="/Users/johnb/mega/awesome.jpg")

Reblogging a Post
~~~~~~~~~~~~~~~~~

Reblog in NPF, using your blog name, the target blog name, and the target post ID:

.. code:: python

    client.reblog_post(blogName, 'blog_to_reblog_from', 125356)

Reblogging a post requires a reblog key and (in NPF) a blog UUID.  These can only be obtained via a GET request on the post.

Under the hood, the client will send this GET request if it doesn't have the key and UUID.  These values are cached, so this will only happen once per client object and post.

Reblog in legacy:

.. code:: python

    client.legacy_reblog(blogName, id=125356, reblog_key="reblog_key")

Other methods
-----------------

Deleting a post
~~~~~~~~~~~~~~~

Deleting just requires that you own the post and have the post id

.. code:: python

    client.delete_post(blogName, 123456) # Deletes your post :(

A note on tags: When passing tags, as params, please pass them as a list (not a comma-separated string):

.. code:: python

    client.create_text(blogName, tags=['hello', 'world'], ...)

Getting notes for a post
~~~~~~~~~~~~~~~~~~~~~~~~

In order to get the notes for a post, you need to have the post id and the blog that it is on.

.. code:: python

    data = client.notes(blogName, id='123456')

The results include a timestamp you can use to make future calls.

.. code:: python

    data = client.notes(blogName, id='123456', before_timestamp=data["_links"]["next"]["query_params"]["before_timestamp"])

Getting notifications
~~~~~~~~~~~~~~~~~~~~~~~~

Notifications are the items that appear on a user's activity page.  You can fetch them like this:

.. code:: python

    data = client.notifications(blogName)

The results include a timestamp you can use to make future calls.

.. code:: python

    data = client.notifications(blogName, before=data["_links"]["next"]["query_params"]["before"])

Tagged Methods
~~~~~~~~~~~~~~

.. code:: python

    # get posts with a given tag
    client.tagged(tag, **params)

Using the interactive console
-----------------------------

This client comes with a nice interactive console to run you through the OAuth process, grab your tokens (and store them for future use).

You'll need ``pyyaml`` installed to run it, but then it's just:

.. code:: bash

    $ python interactive-console.py

and away you go! Tokens are stored in ``~/.tumblr`` and are also shared by other Tumblr API clients like the Ruby client.

Running tests
-------------

The tests (and coverage reports) are run with nose, like this:

.. code:: bash

    python setup.py test

Copyright and license
=====================

Copyright 2021 nostalgebraist

Copyright 2013 Tumblr, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

http://www.apache.org/licenses/LICENSE-2.0

The Initial Developer of some parts of the framework, which are copied from, derived from, or
inspired by Pytumblr (via Apache Flex), is Tumblr, Inc. (https://www.tumblr.com/).

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations.

.. |Build Status| image:: https://app.travis-ci.com/nostalgebraist/pytumblr2.png?branch=master
   :target: https://app.travis-ci.com/nostalgebraist/pytumblr2
