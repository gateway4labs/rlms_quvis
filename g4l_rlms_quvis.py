# -*-*- encoding: utf-8 -*-*-

import requests
import re
from bs4 import BeautifulSoup

from labmanager.forms import AddForm
from labmanager.rlms import register, Laboratory, get_cached_session, GlobalCache
from labmanager.rlms.base import BaseRLMS, BaseFormCreator, Versions

class QuVisAddForm(AddForm):

    DEFAULT_URL = 'http://www.st-andrews.ac.uk/physics/quvis/'
    DEFAULT_LOCATION = 'St Andrews (ScotLand)'
    DEFAULT_PUBLICLY_AVAILABLE = True
    DEFAULT_PUBLIC_IDENTIFIER = 'quvis'
    DEFAULT_AUTOLOAD = True

    def __init__(self, add_or_edit, *args, **kwargs):
        super(QuVisAddForm, self).__init__(*args, **kwargs)
        self.add_or_edit = add_or_edit

    @staticmethod
    def process_configuration(old_configuration, new_configuration):
        return new_configuration

class QuVisFormCreator(BaseFormCreator):

    def get_add_form(self):
        return QuVisAddForm

FORM_CREATOR = QuVisFormCreator()

# URLs:
# http://www.st-andrews.ac.uk/physics/quvis/simulations_twolev/
# http://www.st-andrews.ac.uk/physics/quvis/simulations_html5/sims/

def _extract_links(cached_session, url, extension):
    index_html = cached_session.get(url).text
    soup = BeautifulSoup(index_html)
    links = []
    for anchor in soup.find_all("a"):
        link = anchor.get("href")
        if not link.startswith('?') and not link.startswith('/') and not link.startswith('http://') and not link.startswith('https://') and link.endswith(extension):
            links.append(url + link)
            
    return links


def get_html5_listing(cached_session):
    HTML5_URL = "http://www.st-andrews.ac.uk/physics/quvis/simulations_html5/sims/"
    html5_links = CACHE.get(HTML5_URL)
    if html5_links:
        return html5_links

    folder_links = _extract_links(cached_session, HTML5_URL, '/')
    all_links = {}
    for folder_link in folder_links:
        folder_name = folder_link.rsplit('/',2)[1]
        folder_name = folder_name.replace('-',' ').replace('_',' ')
        folder_name = re.sub("([a-z])([A-Z])","\g<1> \g<2>",folder_name)
        current_folder_links = _extract_links(cached_session, folder_link, '.html')
        current_folder_links.extend(_extract_links(cached_session, folder_link, '.htm'))
        if current_folder_links:
            all_links[folder_name] = current_folder_links[0]

    CACHE.save(HTML5_URL, all_links)
    return all_links

def get_flash_listing(cached_session):
    FLASH_URL = "http://www.st-andrews.ac.uk/physics/quvis/simulations_twolev/"
    flash_links = CACHE.get(FLASH_URL)
    if flash_links:
        return flash_links

    raw_flash_links = _extract_links(cached_session, FLASH_URL, '.swf')
    flash_links = {}
    for raw_flash_link in raw_flash_links:
        lab_name = raw_flash_link.rsplit('/',1)[1]
        if '.' in lab_name:
            lab_name = lab_name.rsplit('.',1)[0]
        lab_name = requests.utils.unquote(lab_name)
        if lab_name.startswith('IOP - '):
            lab_name = lab_name[len('IOP - '):]
        flash_links[lab_name] = raw_flash_link

    CACHE.save(FLASH_URL, flash_links)
    return flash_links

def get_lab_listing():
    cached_session = get_cached_session()
    lab_links = get_html5_listing(cached_session)
    lab_links.update(get_flash_listing(cached_session))
    return lab_links

class RLMS(BaseRLMS):

    def __init__(self, configuration):
        pass

    def get_version(self):
        return Versions.VERSION_1

    def get_capabilities(self):
        return [] 

    def get_laboratories(self):
        labs = []
        for lab_name, lab_link in get_lab_listing().iteritems():
            labs.append(Laboratory(lab_name, lab_link, autoload = True))
        return labs 

    def reserve(self, laboratory_id, username, institution, general_configuration_str, particular_configurations, request_payload, user_properties, *args, **kwargs):
        url = laboratory_id
        return {
            'reservation_id' : requests.utils.quote(url, ''),
            'load_url' : url
        }

register("QuVis", ['1.0'], __name__)
CACHE = GlobalCache("QuVis - 1.0")

def main():
    rlms = RLMS("{}")
    laboratories = rlms.get_laboratories()
    print len(laboratories)
    print
    print laboratories[:10]
    print
    for lab in laboratories[:5]:
        print rlms.reserve(lab.laboratory_id, 'tester', 'foo', '', '', '', '')

if __name__ == '__main__':
    main()
