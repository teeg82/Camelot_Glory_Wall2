"""Responsible for rendering wiki template and pushing to camelot wiki."""

from jinja2 import Environment, FileSystemLoader, select_autoescape

from db import GloryWall
import mechanize
import cookielib
import sys


reload(sys)
sys.setdefaultencoding('utf8')


WIKI_GLORY_WALL_URL = "https://camelot.miraheze.org/w/index.php?title=Glory_Wall&action=edit"


cook = cookielib.CookieJar()
req = mechanize.Browser()
req.set_cookiejar(cook)


env = Environment(
    loader=FileSystemLoader('/glory_wall/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


template = env.get_template("glory_wall.wiki.template")


def render_to_wiki(categories):
    """Render the wiki template and pushes to the camelot wiki."""
    wiki_markup = template.render(categories=categories, GloryWall=GloryWall)
    _write_to_wiki(wiki_markup)
    print(wiki_markup)


def _write_to_wiki(wiki_markup):
    req.open(WIKI_GLORY_WALL_URL)
    req.select_form(name="editform")
    req.form['wpTextbox1'] = wiki_markup
    req.submit()
