from functools import wraps
from copy import deepcopy
from typing import NamedTuple

from .format_conversion.npf2html import TumblrThread


class PostIdentifier(NamedTuple):
    blog_name: str
    id: int

    @staticmethod
    def from_url(url: str) -> 'PostIdentifier':
        url_content = url.partition("//")[2]
        url_paths = url_content.split("/")
        blog_name = url_paths[0].partition('.tumblr.com')[0]

        id_str = url_paths[2]
        id_ = int(id_str)
        return PostIdentifier(blog_name, id_)

    def fetch(self, client):
        return client.get_single_post(blogname=self.blog_name, id=self.id)


def validate_blogname(fn):
    """
    Decorator to validate the blogname and let you pass in a blogname like:
        client.blog_info('codingjester')
    or
        client.blog_info('codingjester.tumblr.com')
    or
        client.blog_info('blog.johnbunting.me')

    and query all the same blog.
    """

    @wraps(fn)
    def add_dot_tumblr(*args, **kwargs):
        if len(args) > 1 and ("." not in args[1]):
            args = list(args)
            args[1] += ".tumblr.com"
        return fn(*args, **kwargs)

    return add_dot_tumblr


def is_npf(post_payload: dict) -> bool:
    # goals:
    #   - always check whether a paylod is npf in the same way
    #   - edits that "simulate legacy" should not change is_npf(payload)==True
    return "content" in post_payload


def simulate_legacy_payload(post_payload):
    # TODO: is this idempotent?
    payload_is_npf = is_npf(post_payload)

    if payload_is_npf:
        # npf branch
        sim_payload = deepcopy(post_payload)

        if "original_type" in post_payload:
            orig_type = post_payload["original_type"]

            # normalize types
            preferred_type_names = {"note": "answer", "regular": "text"}
            orig_type = preferred_type_names.get(orig_type, orig_type)

            sim_payload["type"] = orig_type
        else:
            print(
                f"no original_type key in payload, have type {post_payload.get('type')}, keys {sorted(post_payload.keys())}"
            )

        thread = TumblrThread.from_payload(post_payload)
        op_content = thread.posts[0].content

        if op_content.has_ask:
            ask_content = op_content.ask_content
            sim_payload["asking_name"] = ask_content.asking_name
            sim_payload["question"] = ask_content.to_html()
            sim_payload["answer"] = op_content.to_html()

        if len(thread.posts) > 1:
            this_reblog = thread.posts[-1]
            comment = this_reblog.to_html()
            sim_payload["reblog"] = {
                "comment": comment,
                # real legacy payloads also have a field "tree_html" field -- does anyone use this?
            }

        body = thread.to_html()
        # for some legacy post types, "body" is unused and a type-specific field name is used instead
        # for ease of use, we'll always populate "body" but also try to populate the others for clients who expect them
        sim_payload["body"] = body

        legacy_type_to_body_key = {
            "photo": "caption",
            "audio": "caption",
            "video": "caption",
            "link": "description",
        }
        if sim_payload["type"] in legacy_type_to_body_key:
            body_field = legacy_type_to_body_key[sim_payload["type"]]
            sim_payload[body_field] = body
    else:
        # legacy branch: return as is
        sim_payload = post_payload

    # validate
    if is_npf(sim_payload) != payload_is_npf:
        raise ValueError(
            f"simulated payload switched the value of is_npf: payload {repr(post_payload)} sim_payload {repr(sim_payload)}"
        )
    return sim_payload
