# personal-site

A static site generator based on [makesite](https://github.com/sunainapai/makesite), with many [changes](#differences-from-the-makesite-project).


## Setup

This project has dependencies other than Python itself, so create a venv for it. Use python 3.10 or newer. A  `.tool-versions` file exists for managing the Python version with [asdf](https://asdf-vm.com/).

`python -m venv venv`

Dependencies are listed in the pyproject.toml file and managed with [pip-tools](https://github.com/jazzband/pip-tools). 

To install pip-tools and all dependencies, run `./script/local-setup`

There's also a github actions workflow, which runs tests when the code is pushed to github. It uses `script/gh-dependencies` to install dependencies from the requirements file generated by `local-setup`.

The others in `script/` can be run both locally and by the github actions workflow.

## Usage

`./script/server` runs all the tests, generates the site into `_site`, and serves it on http://localhost:8000

There's no hot reload mechanism built in, but something like [entr](https://jvns.ca/blog/2020/06/28/entr/) can be used to achieve this.

## Differences from the makesite project

A non-exhaustive list:

- `make` is replaced with bash scripts and a github workflow.
- No attempt is made to remain compatible with pure POSIX or with unsupported Python versions.
- [Markdown](https://commonmark.org/) is the assumed format for all posts, and [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/) replaces the deprecated [commonmark](https://commonmarkpy.readthedocs.io/en/latest/index.html) This also enables smart quotes and other typographic niceties.
- A post summary contains the first paragraph of the post, and it will render markdown and html.
- Tests use pytest and have been rewritten for it as needed.
- A working directory path is configured, primarily so tests can always use a proper tmp directory and not touch the actual site output when run.
- The home page is the blog index page.
- `page.html` has a more modern and extensive set of `<head>` elements, including favicons. 
- It almost goes without saying, but the design of the site is different. CSS is based on the original file and [simple.css](https://simplecss.org/), but it has diverged greatly. 

## License

This is free and open source software. You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the [MIT License](LICENSE.md).

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied. See the [MIT License](LICENSE.md) for details.
