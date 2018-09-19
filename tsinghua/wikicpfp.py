# WikiCFP抓取
import requests
from lxml import etree
import time

class thConference:
    """
    每一届具体会议的对象
    """
    def __init__(self, name, link, when, where, submission_deadline, notification_due, final_version_due):
        self.name = name
        self.link = link
        self.when = when
        self.where = where
        self.submission_deadline = submission_deadline
        self.notification_due = notification_due
        self.final_version_due = final_version_due

class Conference:
    def __init__(self, name:'会议全程'=None, abbr:'会议别称'=None, link:'链接地址'=None, past=None, future=None, event:list()=None):
        self.name = name
        self.abbr = abbr
        self.link = link
        self.past = past
        self.future = future
        self.event = event


domin = 'http://www.wikicfp.com/'
urls = ['http://www.wikicfp.com/cfp/series?t=c&i='+chr(i) for i in range(65,65+26)]

confs = []
for url in urls:
    response = requests.get(url)
    page = etree.HTML(response.text)
    bgcolors = ['#f6f6f6', '#e6e6e6']
    for bgcolor in bgcolors:
        a_s = page.xpath('//tr[@bgcolor="'+bgcolor+'"]/td/a')
        tds = page.xpath('//tr[@bgcolor="'+bgcolor+'"]/td/text()')
        # a_s = [s.strip() for s in a_s if s != '\n']
        tds = [s.replace('-','').strip() for s in tds if s != '\n']
        print(len(a_s),len(tds))
        for a,td in zip(a_s,tds):
            confs.append(Conference(name=td, abbr=a.text, link=domin+a.attrib['href']))

    [print(c.abbr, c.name, c.link ,sep=':') for c in confs]
    print('Doen',len(confs))
    break