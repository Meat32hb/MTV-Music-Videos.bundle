# FOUND THAT THERE ARE STILL ANOTHER GROUP OF MUSIC VIDEOS THAT ARE NOT SUPPORTED BY THE URL SERVICE
# WHICH ARE TOPSPIN VIDEOS. They ALL SEEM TO HAVE /ARTIST/ IN THE URL SO I EXCLUDED THEM
# EX 'http://www.mtv.com/artists/the-material/tracks/210716/'

PREFIX = "/video/MTV"
TITLE = "MTV Music Videos"
MTV_ROOT            = "http://www.mtv.com"
MTV_VIDEO_PICKS     = "http://www.mtv.com/music/videos"
MTV_VIDEO_PREMIERES = "http://www.mtv.com/music/videos/premieres"
MTV_VIDEO_TOPRATED  = "http://www.mtv.com/music/video/popular.jhtml"
MTV_VIDEO_YEARBOOK  = "http://www.mtv.com/music/yearbook/"
MTV_VIDEO_DIRECTORY = "http://www.mtv.com/music/video/browse.jhtml?chars=%s"
MTV_ARTIST = "http://www.mtv.com/artists/"
MTV_ARTIST_GENRE = "http://www.mtv.com/artists/genre/"
MTV_MOST_RECENT = 'http://www.mtv.com/music/home/ajax/mostRecent'
MTV_POPULAR = 'http://www.mtv.com/most-popular/music-videos/?metric=numberOfViews&range=%s&order=desc'
MTV_PLAYLIST = 'http://www.mtv.com/global/music/videos/ajax/playlist.jhtml?feo_switch=true&channelId=1&id=%s'

RE_YEARID  = Regex('contentId=(.+?)&year=')
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'

####################################################################################################
def Start():
  ObjectContainer.title1 = TITLE

  HTTP.Headers['User-Agent'] = USER_AGENT
  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_PICKS, title="Top Picks"), title="Top Picks"))
    oc.add(DirectoryObject(key=Callback(SpecialVideos, title="Most Recent Videos", url=MTV_MOST_RECENT), title="Most Recent Videos"))
    oc.add(DirectoryObject(key=Callback(MostPopularMain), title="Most Popular Videos"))
    oc.add(DirectoryObject(key=Callback(ArtistMain), title="Artists"))
    oc.add(DirectoryObject(key=Callback(Yearbook), title="Yearbook"))
    return oc

####################################################################################################
@route(PREFIX + '/mostpopularmain')
def MostPopularMain():
    oc = ObjectContainer()
    time = ["today", "week", "month"]
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[0], title="Most Popular Today"), title="Most Popular Today"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[1], title="Most Popular This Week"), title="Most Popular This Week"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[2], title="Most Popular This Month"), title="Most Popular This Month"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_TOPRATED, title="Most Popular All Time"), title="Most Popular All Time"))
    return oc
####################################################################################################
@route(PREFIX + '/artistmain')
def ArtistMain():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST + 'popular/', title="Most Popular Artist"), title="Most Popular Artist"))
    oc.add(DirectoryObject(key=Callback(ArtistAlphabet), title="Artists A to Z"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST + 'emerging/', title="Emerging Artists"), title="Emerging Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistGenre), title="Artists By Genre"))
    return oc
####################################################################################################
@route(PREFIX + '/artistgenre')
def ArtistGenre():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'rock/', title="Rock Artists"), title="Rock Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'hip-hop/', title="Hip-Hop Artists"), title="Hip-Hop Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'indie/', title="Indie Artists"), title="Indie Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'electronic/', title="Electronic/EDM Artists"), title="Electronic/EDM Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'country/', title="Country Artists"), title="Country Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST_GENRE + 'pop/', title="Pop Artists"), title="Pop Artists"))
    return oc
####################################################################################################
@route(PREFIX + '/videopage')
def VideoPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//ol/li[@itemtype="http://schema.org/VideoObject"]'):
        try:
          link = item.xpath('./div/a//@href')[0]
          if not link.startswith('http://'):
            link = MTV_ROOT + link
          else:
            pass
        except:
          continue
        try:
          image = item.xpath('./div/a/img//@src')[0]
          if not image.startswith('http://'):
            image = MTV_ROOT + image
        except:
          image = ''
        try:
          video_title = item.xpath('./div/a/img//@alt')[0]
        except:
          try:
            video_title = item.xpath('./div/meta[@itemprop="name"]//@content')[0].strip()
          except:
            video_title = None
        if video_title == None or len(video_title) == 0:
            video_title = item.xpath('div/a/img//@alt')[-1]
        try:
          date = Datetime.ParseDate(item.xpath('./p/span/time[@itemprop="datePublished"]//text()')[0].date())
        except:
          date = None
        oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))
    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
    
####################################################################################################
@route(PREFIX + '/yearbook')
def Yearbook():
    oc = ObjectContainer(title2="Yearbook")
    for year in HTML.ElementFromURL(MTV_VIDEO_YEARBOOK).xpath("//div[@class='group-a']/ul/li/a"):
        link = year.get('href')
        if not link.startswith('http://'):
          link = MTV_ROOT + link
        title = year.text.replace(' Videos of ','')
        section_id = RE_YEARID.search(link).group(1)
        Log ('the value of section_id is %s' %section_id)
        url = MTV_PLAYLIST %section_id

        oc.add(DirectoryObject(key=Callback(SpecialVideos, url=url, title=title), title=title))
    return oc
    
####################################################################################################
@route(PREFIX + '/artistalphabet')
def ArtistAlphabet():
    oc = ObjectContainer(title2="Artists")
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ#'):
        oc.add(DirectoryObject(key=Callback(Artists, ch=ch), title=ch))
    return oc

####################################################################################################
@route(PREFIX + '/artists')
def Artists(ch):
    oc = ObjectContainer(title2="Artists: %s" % ch)
    url = MTV_VIDEO_DIRECTORY % ch
    for artist in HTML.ElementFromURL(url).xpath("//ol/li//a"):
        url = MTV_ROOT + artist.get('href')
        # A few artist page links have a url ending in artist.jhtml that resolves to the mtv artist page url
        # so we have to replace the urls here and we add music to take it to the music video page
        if '.jhtml' in url:
          url = url.replace('artist.jhtml', '')
        url = url + 'music-videos/'
        title = artist.text
        oc.add(DirectoryObject(key=Callback(ArtistVideoPage, pageUrl=url, title=title), title=title))
    if len(oc)==0:
      return ObjectContainer(header="Error", message="No artist in this category")
    else:
      return oc

####################################################################################################
@route(PREFIX + '/artistpages')
def ArtistsPages(pageUrl, title):
    oc = ObjectContainer(title2=title)
    # there are a few bad urls in the artsit page, we try to resolve them above but some still fail
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//ul/li[@duration="null"]'):
      url = item.xpath('./meta[@itemprop="url"]')[0].get('content')
      if '.jhtml' in url:
        url = url.replace('artist.jhtml', '')
      url = url + 'music-videos/'
      image = item.xpath('./a/div/div/img')[0].get('src')
      image = image.split('?')[0]
      title = item.xpath('./meta[@itemprop="name"]')[0].get('content')
      oc.add(DirectoryObject(key=Callback(ArtistVideoPage, pageUrl=url, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc

####################################################################################################
# Looked at combining this with VideoPage function, but just different enough to need a separate function
@route(PREFIX + '/artistvideopage')
def ArtistVideoPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    # there are a few bad urls in the artsit page, we try to resolve them above but some still fail
    try:
      content = HTML.ElementFromURL(pageUrl)
    except:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    for item in content.xpath('//ul/li[@type="videos"]'):
      try:
        link = item.xpath('./a//@href')[0]
        if not link.startswith('http://'):
          link = MTV_ROOT + link
      except:
        continue
      # SOME VIDEOS ARE topspin videos (have /artists/ in the video url) are listed here and they are not supported by the URL service
      if not '/artists/' in link:
        # A few artist pages do not have thumbnail itemprop so added alternate thumb location
        try:
          image = item.xpath('./meta[@itemprop="thumbnail"]//@content')[0]
        except:
          try:
            image = item.xpath('./a/div/div/img//@src')[0]
            image = image.split('?')[0]
          except:
            image = ''
        # found one with a blank title
        try:
          video_title = item.xpath('./meta[@itemprop="name"]//@content')[0]
        except:
          try:
            video_title = item.xpath('./a/div/div/img//@alt')[0]
          except:
            video_title = ''
        artist = title
        video_title = "%s - %s" % (artist, video_title)
        oc.add(VideoClipObject(url=link, title=video_title, thumb=Resource.ContentsOfURLWithFallback(url=image)))
      else:
        pass
    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
####################################################################################################
@route(PREFIX + '/specialvideos')
def SpecialVideos(url, title):
    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(url)
    for item in content.xpath('//ol/li'):
      try:
        url = item.xpath('./div/a//@href')[0]
        if not url.startswith('http://'):
          url = MTV_ROOT + url
      except:
        continue
      # SOME NEWER VIDEOS ARE topspin videos (have /artists/ in the video url) and they are not supported by the URL service
      if not '/artists/' in url:
        try:
          image = item.xpath('./div/a/img//@src')[0]
          image = image.split('?')[0]
        except:
          image = ''
        try:
          title = item.xpath('./div/a/img//@alt')[0].strip()
        except:
          try:
            title = item.xpath('./div/a/strong/text()')[0].strip()
          except:
            title = None
        oc.add(VideoClipObject(url=url, title=title, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
