#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2022 Keith R. Petersen
#
# This software is a derivative of the original makesite.py.
# The license text of the original makesite.py is included below.
#
# Copyright (c) 2018 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Make static website/blog with Python."""


import os
from pathlib import Path
import shutil
import re
import glob
import sys
import json
import datetime

from lxml import html
from markdown_it import MarkdownIt


def fread(filename):
    """Read file and close the file."""
    with open(filename, "r") as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, "w") as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + "\n")


def get_post_first_p(text):
    """Get the first p from the post as html."""
    rendered_html = render_md(text)
    tree = html.fromstring(rendered_html)
    first_p = html.tostring(
        tree.xpath("/descendant::p[1]")[0], encoding="unicode"
    ).strip()

    return first_p


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r"\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+", text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


def render_md(input):
    md = MarkdownIt("commonmark", {"typographer": True})
    md.enable(["replacements", "smartquotes"])
    return md.render(input)


def read_content(filename):
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split(".")[0]
    match = re.search(r"^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$", date_slug)
    content = {
        "date": match.group(1) or "1970-01-01",
        "slug": match.group(2),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # assume all content is in markdown
    text = render_md(text)

    # Update the dictionary with content and RFC 2822 date.
    content.update({"content": text, "rfc_2822_date": rfc_2822_format(content["date"])})

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(
        r"{{\s*([^}\s]+)\s*}}",
        lambda match: str(params.get(match.group(1), match.group(0))),
        template,
    )


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get("render") == "yes":
            rendered_content = render(page_params["content"], **page_params)
            page_params["content"] = rendered_content
            content["content"] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log("Rendering {} => {} ...", src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x["date"], reverse=True)


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    items = []
    for post in posts:
        item_params = dict(params, **post)
        item_params["summary"] = get_post_first_p(post["content"])
        item = render(item_layout, **item_params)
        items.append(item)

    params["content"] = "".join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log("Rendering list => {} ...", dst_path)
    fwrite(dst_path, output)


def main(working_path: Path = Path.cwd()):
    output_path = working_path / "_site"

    # Create a new _site directory from scratch.
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    shutil.copytree("static", output_path)

    # Default parameters.
    params = {
        "base_path": "",
        "subtitle": "Software Engineer",
        "author": "Keith R. Petersen",
        "site_url": "http://localhost:8000",
        "current_year": datetime.datetime.now().year,
    }

    # If params.json exists, load it.
    params_path = working_path / "params.json"
    if params_path.exists():
        params.update(json.loads(fread(params_path)))

    # Load layouts.
    page_layout = fread("layout/page.html")
    post_layout = fread("layout/post.html")
    list_layout = fread("layout/list.html")
    item_layout = fread("layout/item.html")
    feed_xml = fread("layout/feed.xml")
    item_xml = fread("layout/item.xml")

    # Combine layouts to form final layouts.
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)

    # Create blogs.
    blog_posts = make_pages(
        f"{working_path}/content/blog/*.md",
        output_path.as_posix() + "/blog/{{ slug }}/index.html",
        post_layout,
        blog="blog",
        **params,
    )

    # Create blog list pages.
    make_list(
        blog_posts,
        f"{output_path}/index.html",
        list_layout,
        item_layout,
        blog="blog",
        title="Blog",
        **params,
    )

    # Create RSS feeds.
    make_list(
        blog_posts,
        f"{output_path}/rss.xml",
        feed_xml,
        item_xml,
        blog="blog",
        title="Blog",
        **params,
    )

    # Create site pages.
    make_pages(
        f"{working_path}/content/[!_]*.html",
        output_path.as_posix() + "/{{ slug }}/index.html",
        page_layout,
        **params,
    )


if __name__ == "__main__":
    main()
