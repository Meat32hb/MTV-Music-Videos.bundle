import re

MTV_PLUGIN_PREFIX   = "/video/MTV"
MTV_ROOT            = "http://www.mtv.com"
MTV_VIDEO_PICKS     = "http://www.mtv.com/music/videos"
MTV_VIDEO_PREMIERES = "http://www.mtv.com/music/videos/premieres"
MTV_VIDEO_TOPRATED  = "http://www.mtv.com/music/video/popular.jhtml"
MTV_VIDEO_YEARBOOK  = "http://www.mtv.com/music/yearbook/"
MTV_VIDEO_DIRECTORY = "http://www.mtv.com/music/video/browse.jhtml?chars=%s"

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MTV_PLUGIN_PREFIX, MainMenu, "MTV Music Videos", "icon-default.png", "art-default.jpg")
  ObjectContainer.art = R('art-default.jpg')
  ObjectContainer.title1 = 'MTV Music Videos'
  DirectoryObject.thumb=R("icon-default.png")

  HTTP.Headers['User-Agent'] = USER_AGENT
  HTTP.CacheTime=3600

####################################################################################################
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_PICKS, title="Top Picks"), title="Top Picks"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_PREMIERES, title="Premieres"), title="Premieres"))
    oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl = MTV_VIDEO_TOPRATED, title="Most Popular"), title="Most Popular"))
    oc.add(DirectoryObject(key=Callback(ArtistAlphabet), title="Artists"))
    oc.add(DirectoryObject(key=Callback(Yearbook), title="Yearbook"))
    return oc

####################################################################################################
def VideoPage(pageUrl, title):
    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//div[@class="group-b"]/div/div//ol/li/div'):
        try:
          link = MTV_ROOT + item.xpath("a")[0].get('href')
        except:
          continue
        image = item.xpath("a/img")[0].get('src')
        if not image.startswith('http://'):
          image = MTV_ROOT + image
        title = item.xpath("a")[-1].text.strip()
        if title == None or len(title) == 0:
            title = item.xpath("a/img")[-1].get('alt')
        title = title.replace('"','')
        oc.add(VideoClipObject(url=link, title=title, thumb=Resource.ContentsOfURLWithFallback(url=image, fallback="icon-default.png")))
    if len(oc)==0:
      return ObjectContainer(header="Sorry !", message="No video available in this category.")
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
            link = re.sub('#.*','', url)
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
        title = artist.text
        oc.add(DirectoryObject(key=Callback(VideoPage, pageUrl=url, title=title), title=title))
    if len(oc)==0:
      return ObjectContainer(header="Error", message="No artist in this category")
    else:
      return oc
