# FOUND THAT THERE ARE STILL ANOTHER GROUP OF MUSIC VIDEOS THAT ARE NOT SUPPORTED BY THE URL SERVICE
# WHICH ARE TOPSPIN VIDEOS. They ALL SEEM TO HAVE /ARTIST/ IN THE URL SO I EXCLUDED THEM
# EX 'http://www.mtv.com/artists/the-material/tracks/210716/'

MTV_PLUGIN_PREFIX   = "/video/MTV"
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

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MTV_PLUGIN_PREFIX, MainMenu, "MTV Music Videos", "icon-default.png", "art-default.jpg")
  ObjectContainer.art = R('art-default.jpg')
  ObjectContainer.title1 = 'MTV Music Videos'
  DirectoryObject.thumb=R("icon-default.png")

  HTTP.Headers['User-Agent'] = USER_AGENT
  #HTTP.CacheTime=3600

####################################################################################################
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_PICKS, title="Top Picks"), title="Top Picks"))
    oc.add(DirectoryObject(key=Callback(MostRecent, title="Most Recent Videos"), title="Most Recent Videos"))
    oc.add(DirectoryObject(key=Callback(MostPopularMain), title="Most Popular Videos"))
    oc.add(DirectoryObject(key=Callback(ArtistMain), title="Artists"))
    oc.add(DirectoryObject(key=Callback(Yearbook), title="Yearbook"))
    return oc

####################################################################################################
def MostPopularMain():
    oc = ObjectContainer()
    time = ["today", "week", "month"]
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[0], title="Most Popular Today"), title="Most Popular Today"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[1], title="Most Popular This Week"), title="Most Popular This Week"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_POPULAR %time[2], title="Most Popular This Month"), title="Most Popular This Month"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_TOPRATED, title="Most Popular All Time"), title="Most Popular All Time"))
    return oc
####################################################################################################
def ArtistMain():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST + 'popular/', title="Most Popular Artist"), title="Most Popular Artist"))
    oc.add(DirectoryObject(key=Callback(ArtistAlphabet), title="Artists A to Z"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, pageUrl = MTV_ARTIST + 'emerging/', title="Emerging Artists"), title="Emerging Artists"))
    oc.add(DirectoryObject(key=Callback(ArtistGenre), title="Artists By Genre"))
    return oc
####################################################################################################
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
def VideoPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//div[@class="group-b"]/div/div//ol/li/div'):
        try:
          link = item.xpath("a")[0].get('href')
          if not link.startswith('http://'):
            link = MTV_ROOT + link
          else:
            pass
        except:
          continue
        try:
          image = item.xpath("a/img")[0].get('src')
        except:
          image = ''
        if not image.startswith('http://'):
          image = MTV_ROOT + image
        try:
          video_title = item.xpath('.//meta[@itemprop="name"]')[0].get('content')
        except:
          if '/artist/' in pageUrl:
            artist = title
            video_title = item.xpath('.//a/text()')[0].strip()
            video_title = "%s - %s" % (artist, video_title)
          else:
            video_title = item.xpath('.//a/img')[0].get('alt')
        if video_title == None or len(video_title) == 0:
            video_title = item.xpath("a/img")[-1].get('alt')
        video_title = video_title.replace('"','')
        try:
          date = Datetime.ParseDate(item.xpath('.//time[@itemprop="datePublished"]')[0].text).date()
        except:
          date = None
        oc.add(VideoClipObject(url=link, title=video_title, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback="icon-default.png")))
    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
    
####################################################################################################
def Yearbook():
    oc = ObjectContainer(title2="Yearbook")
    for year in HTML.ElementFromURL(MTV_VIDEO_YEARBOOK).xpath("//div[@class='group-a']/ul/li/a"):
        link = MTV_ROOT + year.get('href')
        title = year.text.replace(' Videos of ','')
        oc.add(DirectoryObject(key=Callback(YearPage, pageUrl=link, title=title), title=title))
    return oc
    
####################################################################################################
def YearPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    for video in HTML.ElementFromURL(pageUrl).xpath("//div[@class='mdl']//ol/li"):
        url = MTV_ROOT + video.xpath('.//a')[0].get('href')
        img = video.xpath('.//a/img')[0]
        title = img.get('alt')
        if title != None:
            title = title.strip('"').replace('- "','- ').replace(' "',' - ')
            thumb = MTV_ROOT + img.get('src')
            link = url.split('#')[0]
            oc.add(VideoClipObject(url=link, title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback="icon-default.png")))
    return oc

####################################################################################################
def ArtistAlphabet():
    oc = ObjectContainer(title2="Artists")
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ#'):
        oc.add(DirectoryObject(key=Callback(Artists, ch=ch), title=ch))
    return oc

####################################################################################################
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
def ArtistVideoPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    # there are a few bad urls in the artsit page, we try to resolve them above but some still fail
    try:
      content = HTML.ElementFromURL(pageUrl)
    except:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    for item in content.xpath('//ul/li[@type="videos"]'):
      link = item.xpath("a")[0].get('href')
      if not link.startswith('http://'):
        link = MTV_ROOT + link
	  # SOME VIDEOS ARE topspin videos (have /artists/ in url) are listed here and they are not supported by the URL service
      if not '/artists/' in link:
        # A few artist pages do not have thumbnail itemprop so added alternate thumb location
        try:
          image = item.xpath('.//meta[@itemprop="thumbnail"]')[0].get('content')
        except:
          image = item.xpath('./a/div/div/img')[0].get('src')
        image = image.split('?')[0]
        # found one with a blank title
        try:
          video_title = item.xpath('.//meta[@itemprop="name"]')[0].get('content')
        except:
          video_title = ''
        artist = title
        oc.add(VideoClipObject(url=link, title=video_title, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback="icon-default.png")))
    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
####################################################################################################
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
      oc.add(DirectoryObject(key=Callback(ArtistVideoPage, pageUrl=url, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback="icon-default.png")))

    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc

####################################################################################################
def MostRecent(title):
    oc = ObjectContainer(title2=title)
    # there are a few bad urls in the artsit page, we try to resolve them above but some still fail
    content = HTML.ElementFromURL(MTV_MOST_RECENT)
    for item in content.xpath('//ol/li'):
      url = item.xpath('./div/a//@href')[0]
      # adding check for unnaccepted urls
      if not '/artists/' in url:
        image = item.xpath('./div/a/img//@src')[0]
        image = image.split('?')[0]
        title = item.xpath('./div/a//text()')[0]
        title = title.strip()
        oc.add(VideoClipObject(url=url, title=title, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback="icon-default.png")))

    if len(oc)==0:
      return ObjectContainer(header="Sorry!", message="No video available in this category.")
    else:
      return oc
