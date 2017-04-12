from bs4 import BeautifulSoup
import re
import json
import requests
import time

'''
Currently not doing any error handling
Will fix before implementing into malstats
'''
class MALMangaScraper():

    def __init__(self, mangaID):
        # soup is the backbone for all class methods
        # this should be an instance of BeautifulSoup()
        self.soup = None
        self.url = 'https://myanimelist.net/manga/' + mangaID
        self.update_soup()

    def update_soup(self):
        res = requests.get(self.url)
        self.soup = BeautifulSoup(res.content, 'html.parser')

    def set_mangaID(self, mangaID):
        self.url = 'https://myanimelist.net/manga/' + mangaID

    def set_mangaID_and_update(self, mangaID):
        self.url = 'https://myanimelist.net/manga/' + mangaID
        self.update_soup()

    def scrape_manga(self):
        descriptor = {
            'Type'        : self.get_type,
            'Title'       : self.get_title,
            'Title_JP'    : self.get_title_jp,
            'Title_EN'    : self.get_title_en,
            'Chapters'    : self.get_chapters,
            'Status'      : self.get_status,
            'Volumes'     : self.get_premier,
            'Authors'     : self.get_authors,
            'Serial'      : self.get_serialization,
            'Genres'      : self.get_genres,
            'Score'       : self.get_score_as_float,
            'Members'     : self.get_members,
            'Favorites'   : self.get_favorites,
            'Adaptations' : self.get_adaptations
        }

        for key, function in descriptor.items():
            descriptor[key] = function()

        descriptor['Timestamp'] = time.ctime()

        return descriptor

    def get_type(self):
        tag = self.soup.find('span', string='Type:')
        manga_type = None
        if tag:
            manga_type = tag.find_next_sibling('a').string
        return manga_type

    def get_title(self):
        tag = self.soup.find('span', itemprop='name')
        title = None
        if tag:
            title = tag.string.strip()
        return title

    def get_title_jp(self):
        tag = self.soup.find('span', string='Japanese:')
        title = None
        if tag:
            title = tag.next_sibling.encode('utf8')
            title = title.strip()
            return title
        return title

    def get_title_en(self):
        tag = self.soup.find('span', string='English:')
        title = None
        if tag:
            title = tag.next_sibling.encode('utf8')
            title = title.strip()
            return title
        return title

    def get_chapters(self):
        tag = self.soup.find('span', string='Chapters:')
        if tag:
            chaps = tag.next_sibling.encode('utf8')
            try:
                chaps = int(chaps.strip())
                return chaps
            except:
                print "Unable to correctly parse chapters"
        return 0

    def get_status(self):
        tag = self.soup.find('span', string='Status:')
        status = None
        if tag:
            status = tag.next_sibling.encode('utf8')
            status = status.strip()
            return status
        return status

    def get_volumes(self):
        tag = self.soup.find('span', string='Volumes:')
        if tag:
            vols = tag.next_sibling.encode('utf8')
            try:
                vols = int(vols.strip())
                return vols
            except:
                print "Unable to correctly parse volumes"
        return 0

    def get_authors(self):
        mainTag = self.soup.find('span', string='Authors:')
        siblingTags = mainTag.find_next_siblings('a')
        authors = []
        pattern = re.compile('/people/([0-9]+)')
        if not siblingTags:
            print 'Failure retrieving authors'
        else:
            for sib in siblingTags:
                m = re.match(pattern, sib['href'])
                auth_id = 0
                try:
                    auth_id = int(m.group(1))
                except:
                    pass
                authors.append((auth_id, sib.string))

        return authors

    def get_serialization(self):
        mainTag = self.soup.find('span', string='Serialization:')
        siblingTags = mainTag.find_next_siblings('a')
        serial = []
        pattern = re.compile('/manga/magazine/([0-9]+)')
        if not siblingTags:
            print 'Failure retrieving genres'
        else:
            for sib in siblingTags:
                m = re.match(pattern, sib['href'])
                ser_id = 0
                try:
                    ser_id = int(m.group(1))
                except:
                    pass
                serial.append((ser_id, sib.string))

        return serial

    def get_genres(self):
        tags = self.soup(href=re.compile('genre'))
        genres = []
        if not tags:
            print 'Failure retrieving genres'
        else:
            for tag in tags:
                genres.append(tag.string)
        return genres

    def get_score_as_float(self):
        tag = self.soup.find('span', itemprop='ratingValue')
        score = 0.0
        if tag:
            raw_score = tag.string
            score = float('{0:2s}'.format(raw_score))
        return score

    def get_members(self):
        tag = self.soup.find('span', string='Members:')
        members = 0
        if tag:
            members = tag.next_sibling.replace(',','')
            try:
                members = int(members)
            except:
                pass
        return members

    def get_favorites(self):
        tag = self.soup.find('span', string='Favorites:')
        favs = 0
        if tag:
            fav = tag.next_sibling.replace(',','')
            try:
                favs = int(fav)
            except:
                pass
        return favs

    # This is a fragile method. I should find a better way to do this
    def get_adaptations(self):
        tag = self.soup.find('td', string="Adaptation:")
        pattern = re.compile('/anime/([0-9]+)')
        adapts = []
        if tag:
            sibling = tag.find_parent('tr').find_all('a')
            if not sibling:
                print 'No adaptations found'
                return []
            for link in sibling:
                m = re.match(pattern, link['href'])
                try:
                    anime_id = int(m.group(1))
                    adapts.append((anime_id, link.string))
                except:
                    print 'Unable to parse anime ID'
        return adapts

    def get_prequel(self):
        tag = self.soup.find('td', string="Prequel:")
        pattern = re.compile('/manga/([0-9]+)')
        prequel = []
        if tag:
            parent = tag.find_parent('tr')
            sibling = parent('a', href=pattern)
            if not sibling:
                print 'No prequel found'
                return []
            for link in sibling:
                m = re.match(pattern, link['href'])
                try:
                    manga_id = int(m.group(1))
                    prequel.append((manga_id, link.string))
                except:
                    print 'Unable to parse manga ID'
        return prequel

    def get_spinoffs(self):
        tag = self.soup.find('td', string="Spin-off:")
        pattern = re.compile('/manga/([0-9]+)')
        prequel = []
        if tag:
            parent = tag.find_parent('tr')
            sibling = parent('a', href=pattern)
            if not sibling:
                print 'No prequel found'
                return []
            for link in sibling:
                m = re.match(pattern, link['href'])
                try:
                    manga_id = int(m.group(1))
                    prequel.append((manga_id, link.string))
                except:
                    print 'Unable to parse manga ID'
        return prequel

    def get_others(self):
        tag = self.soup.find('td', string="Other:")
        pattern = re.compile('/manga/([0-9]+)')
        prequel = []
        if tag:
            parent = tag.find_parent('tr')
            sibling = parent('a', href=pattern)
            if not sibling:
                print 'No prequel found'
                return []
            for link in sibling:
                m = re.match(pattern, link['href'])
                try:
                    manga_id = int(m.group(1))
                    prequel.append((manga_id, link.string))
                except:
                    print 'Unable to parse manga ID'
        return prequel

    def get_side_stories(self):
        tag = self.soup.find('td', string="Side story:")
        pattern = re.compile('/manga/([0-9]+)')
        prequel = []
        if tag:
            parent = tag.find_parent('tr')
            print len(list(parent.descendants))
            sibling = parent('a', href=pattern)
            if not sibling:
                print 'No prequel found'
                return []
            for link in sibling:
                m = re.match(pattern, link['href'])
                try:
                    manga_id = int(m.group(1))
                    prequel.append((manga_id, link.string))
                except:
                    print 'Unable to parse manga ID'
        return prequel


scraper = MALMangaScraper('598')
# manga = scraper.scrape_manga()
# manga_as_json = json.dumps(manga)
# print manga_as_json