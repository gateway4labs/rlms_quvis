# -*-*- encoding: utf-8 -*-*-

import requests
import re
from bs4 import BeautifulSoup

from labmanager.forms import AddForm
from labmanager.rlms import register, Laboratory, Capabilities
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

def _extract_links(url, extension):
    index_html = QUVIS.cached_session.timeout_get(url).text
    soup = BeautifulSoup(index_html, "lxml")
    links = []
    for anchor in soup.find_all("a"):
        link = anchor.get("href")
        if not link.startswith('?') and not link.startswith('/') and not link.startswith('http://') and not link.startswith('https://') and link.endswith(extension):
            links.append(url + link)
            
    return links


def get_html5_listing():
    HTML5_URL = "http://www.st-andrews.ac.uk/physics/quvis/simulations_html5/sims/"
    html5_links = QUVIS.cache.get(HTML5_URL)
    if html5_links:
        return html5_links

    folder_links = _extract_links(HTML5_URL, '/')
    all_links = {}
    for folder_link in folder_links:
        folder_name = folder_link.rsplit('/',2)[1]
        folder_name = folder_name.replace('-',' ').replace('_',' ')
        folder_name = re.sub("([a-z])([A-Z])","\g<1> \g<2>",folder_name)
        current_folder_links = _extract_links(folder_link, '.html')
        current_folder_links.extend(_extract_links(folder_link, '.htm'))
        if current_folder_links:
            all_links[folder_name] = current_folder_links[0]

    QUVIS.cache[HTML5_URL] = all_links
    return all_links

def get_flash_listing():
    FLASH_URL = "http://www.st-andrews.ac.uk/physics/quvis/simulations_twolev/"
    flash_links = QUVIS.cache.get(FLASH_URL)
    if flash_links:
        return flash_links

    raw_flash_links = _extract_links(FLASH_URL, '.swf')
    flash_links = {}
    for raw_flash_link in raw_flash_links:
        lab_name = raw_flash_link.rsplit('/',1)[1]
        if '.' in lab_name:
            lab_name = lab_name.rsplit('.',1)[0]
        lab_name = requests.utils.unquote(lab_name)
        if lab_name.startswith('IOP - '):
            lab_name = lab_name[len('IOP - '):]
        flash_links[lab_name] = raw_flash_link

    QUVIS.cache[FLASH_URL] = flash_links
    return flash_links

def get_lab_listing():
    lab_links = get_html5_listing()
    lab_links.update(get_flash_listing())
    return lab_links

class RLMS(BaseRLMS):

    def __init__(self, configuration):
        pass

    def get_version(self):
        return Versions.VERSION_1

    def get_capabilities(self):
        return [ Capabilities.URL_FINDER, Capabilities.CHECK_URLS ]

    def get_base_urls(self):
        return [ 'https://www.st-andrews.ac.uk/physics/quvis/', 'http://www.st-andrews.ac.uk/physics/quvis/' ]

    def get_lab_by_url(self, url):
        http_url = url.replace('https://', 'http://', 1)
        http_url_quoted = requests.utils.quote(url.replace('https://', 'http://', 1), ':/')
        http_url_flash1 = http_url.replace('.html', '.swf')
        http_url_flash2 = http_url.replace('.html', '.swf')
        http_url_quoted_flash1 = http_url_quoted.replace('.html', '.swf')
        http_url_quoted_flash2 = http_url_quoted.replace('.htm', '.swf')
        pack = http_url, http_url_quoted, http_url_flash1, http_url_flash2, http_url_quoted_flash1, http_url_quoted_flash2

        for lab_name, lab_link in get_lab_listing().iteritems():
            http_link = lab_link.replace('https://', 'http://', 1)
            if http_link in pack:
                return Laboratory(lab_name, lab_link, autoload = True)
       
        return None

    def get_laboratories(self):
        labs = []
        for lab_name, lab_link in get_lab_listing().iteritems():
            labs.append(Laboratory(lab_name, lab_link, autoload = True))
        return labs

    def get_check_urls(self, laboratory_id):
        return [ laboratory_id ]

    def reserve(self, laboratory_id, username, institution, general_configuration_str, particular_configurations, request_payload, user_properties, *args, **kwargs):
        url = laboratory_id
        return {
            'reservation_id' : requests.utils.quote(url, ''),
            'load_url' : url
        }

def populate_cache():
    get_lab_listing()

QUVIS = register("QuVis", ['1.0'], __name__)
QUVIS.add_global_periodic_task('Populating cache', populate_cache, minutes = 55)

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
