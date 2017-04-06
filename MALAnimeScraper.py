from bs4 import BeautifulSoup
import re

class MALAnimeScraper():

    def __init__(soup):
        self.soup = self.soup

    def get_type(soup):
        tag = self.soup.find('span', string='Type:')
        anime_type = None
        if tag:
            anime_type = tag.find_next_sibling('a').string
        return anime_type

    def get_title(soup):
        tag = self.soup.find('span', itemprop='name')
        title = None
        if tag:
            title = tag.string.strip()
        return title

    def get_title_jp(soup):
        tag = self.soup.find('span', string='Japanese:')
        title = None
        if tag:
            title = tag.next_sibling.encode('utf8')
            title = title.strip()
            return title
        return title

    def get_title_en(soup):
        tag = self.soup.find('span', string='English:')
        title = None
        if tag:
            title = tag.next_sibling.encode('utf8')
            title = title.strip()
            return title
        return title

    def get_episodes(soup):
        tag = self.soup.find('span', string='Episodes:')
        if tag:
            episodes = tag.next_sibling.encode('utf8')
            try:
                episodes = int(episodes.strip())
                return episodes
            except:
                print "Unable to correctly parse episodes"
        return 0

    def get_status(soup):
        tag = self.soup.find('span', string='Status:')
        status = None
        if tag:
            status = tag.next_sibling.encode('utf8')
            status = status.strip()
            return status
        return status

    def get_premier(soup):
        tag = soup.find('span', string='Premiered:')
        prem = None
        if tag:
            next_tag = tag.find_next_sibling('a')
            date, season = next_tag.string.strip().split(' ')
            prem = (date, season)
        return prem

    def get_producers(soup):
        mainTag = self.soup.find('span', string='Producers:')
        siblingTags = mainTag.find_next_siblings('a')
        producers = []
        pattern = re.compile('/anime/producer/([0-9]+)')
        if not siblingTags:
            print 'Failure retrieving genres'
        else:
            for sib in siblingTags:
                m = re.match(pattern, sib['href'])
                prod_id = 0
                try:
                    prod_id = int(m.group(1))
                except:
                    pass
                producers.append((prod_id, sib.string))

        return producers

    def get_studios(soup):
        mainTag = self.soup.find('span', string='Studios:')
        siblingTags = mainTag.find_next_siblings('a')
        studios = []
        pattern = re.compile('/anime/producer/([0-9]+)')
        if not siblingTags:
            print 'Failure retrieving genres'
        else:
            for sib in siblingTags:
                m = re.match(pattern, sib['href'])
                stud_id = 0
                try:
                    stud_id = int(m.group(1))
                except:
                    pass
                studios.append((stud_id, sib.string))

        return studios

    def get_source(soup):
        tag = self.soup.find('span', string='Source:')
        source = None
        if tag:
            source = tag.next_sibling.encode('utf8')
            source = source.strip()
        return source

    def get_genres(soup):
        tags = self.soup(href=re.compile('genre'))
        genres = []
        if not tags:
            print 'Failure retrieving genres'
        else:
            for tag in tags:
                genres.append(tag.string)
        return genres

    def get_duration_minutes(soup):
        tag = self.soup.find('span', string='Duration:')
        duration = -1
        dur_text = None
        if tag:
            dur_text = tag.next_sibling.encode('utf8')
            dur_text = dur_text.strip()
            if dur_text != 'Unknown':
               duration = parse_duration(dur_text)
        return duration

    def get_rating(soup):
        tag = self.soup.find('span', string='Rating:')
        rating = None
        if tag:
            rating = tag.next_sibling.encode('utf8')
            rating = rating.strip()
        return rating

    def get_score_as_float(soup):
        tag = self.soup.find('span', itemprop='ratingValue')
        score = 0.0
        if tag:
            raw_score = tag.string
            score = float('{0:2s}'.format(raw_score))
        return score

    def get_members(soup):
        tag = self.soup.find('span', string='Members:')
        members = 0
        if tag:
            members = tag.next_sibling.replace(',','')
            try:
                members = int(members)
            except:
                pass
        return members

    def get_favorites(soup):
        tag = self.soup.find('span', string='Favorites:')
        favs = 0
        if tag:
            favs = tag.next_sibling.replace(',','')
            try:
                fav = int(fav)
            except:
                pass
        return fav

    def parse_duration(text):
        pattern = re.compile('([\d]+)\D+(?:(\d+))?')
        m = re.match(pattern, text)

        total = 0
        print m.groups()
        all_groups = m.groups()
        if len(all_groups) != 2:
            return 0
        else:
            if not all_groups[1]:
                total = int(all_groups[0])
            else:
                total = int(all_groups[0])*60 + int(all_groups[1])

        return total