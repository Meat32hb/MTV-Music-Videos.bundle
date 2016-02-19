# THERE MAY STILL BE A GROUP OF MUSIC VIDEOS THAT ARE NOT SUPPORTED BY THE URL SERVICE FOR TOPSPIN VIDEOS. 
# CURRENTLY THEY ARE NOT EXCLUDED. AFTER REWRITING THE URL SERVICE, THEY NEED TO BE LOOKED AT AGAIN
# THEY ALL SEEM TO HAVE /ARTIST/ IN THE URL. EX 'http://www.mtv.com/artists/the-material/tracks/210716/'

PREFIX = '/video/mtv'
TITLE = 'MTV Music Videos'
MTV_ROOT = 'http://www.mtv.com'
MTV_VIDEO = 'http://www.mtv.com/music/videos/'
MTV_ARTIST = 'http://www.mtv.com/artists/'
MTV_SEARCH = 'http://search.mtvnservices.com/typeahead/suggest/?spellcheck.count=5&q=%s&siteName=artist_platform&format=json&rows=50'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE

    HTTP.Headers['User-Agent'] = USER_AGENT
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(MusicMain), title="Music Videos"))
    oc.add(DirectoryObject(key=Callback(ArtistMain), title="Artists"))

    return oc

####################################################################################################
@route(PREFIX + '/musicmain')
def MusicMain():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Best New Videos", page_url=MTV_VIDEO, id="profile_latest_music"), title="Best New Videos"))
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Latest Music Videos", page_url=MTV_VIDEO, id="latest-mvd"), title="Latest Music Videos"))
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Most Viewed Music Videos", page_url=MTV_VIDEO, id="most-viewed-mvd"), title="Most Viewed Music Videos"))

    return oc

####################################################################################################
@route(PREFIX + '/artistmain')
def ArtistMain():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ArtistsPages, page_url=MTV_ARTIST + 'popular/', title="Popular Artist"), title="Popular Artist"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, page_url=MTV_ARTIST, title="MTV Picks"), title="MTV Picks"))
    oc.add(DirectoryObject(key=Callback(CollectionsPages, page_url=MTV_ARTIST + 'collections/', title="Collections"), title="Collections"))
    oc.add(DirectoryObject(key=Callback(ArtistsPages, page_url=MTV_ARTIST + '/collections/artist-to-watch/897377/', title="Artist To Watch"), title="Artist To Watch"))
    oc.add(InputDirectoryObject(key=Callback(SearchArtists, title="Search for Artists"), title="Search for Artists", summary="Click here to search for artists", prompt="Search for the artists you would like to find"))

    return oc

####################################################################################################
@route(PREFIX + '/artistpages')
def ArtistsPages(page_url, title):

    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(page_url)

    for item in content.xpath('//ul/li[@data-duration="null"]'):

        link = item.xpath('./meta[@itemprop="url"]/@content')[0]
        image = item.xpath('.//img/@data-original')[0]
        image = image.split('?')[0]
        title = item.xpath('./meta[@itemprop="name"]/@content')[0]
        link = link + 'music/'

        oc.add(DirectoryObject(key=Callback(VideoPage, page_url=link, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        return ObjectContainer(header="Sorry!", message="No video available in this category.")

    return oc

####################################################################################################
@route(PREFIX + '/collectionspages')
def CollectionsPages(page_url, title):

    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(page_url)

    for item in content.xpath('//ul/li[contains(@id, "collection_")]'):

        link = item.xpath('./a/@href')[0]
        if not link.startswith('http://'):
            link = MTV_ROOT + link

        image = item.xpath('.//img/@src')[0]
        image = image.split('?')[0]
        artist_title = item.xpath('.//img/@alt')[0]

        oc.add(DirectoryObject(key=Callback(ArtistsPages, page_url=link, title=artist_title), title=artist_title, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        return ObjectContainer(header="Sorry!", message="No video available in this category.")

    return oc

####################################################################################################
@route(PREFIX + '/searchartists')
def SearchArtists(title, query):

    oc = ObjectContainer(title2=title)
    url = MTV_SEARCH % (String.Quote(query, usePlus=True))
    json = JSON.ObjectFromURL(url)

    for artist in json['response']['docs']:

        url = MTV_ARTIST + artist['platform_artist_alias_s'] + '/music/'
        title = artist['artist_name_s']

        oc.add(DirectoryObject(key=Callback(VideoPage, page_url=url, title=title), title=title))

    if len(oc) < 1:
        return ObjectContainer(header="Sorry!", message="No artist in this category")

    return oc

####################################################################################################
# Looked at combining this with VideoPage function, but just different enough to need a separate function
@route(PREFIX + '/videopage')
def VideoPage(page_url, title, id=''):

    oc = ObjectContainer(title2=title)

    try:
        content = HTML.ElementFromURL(page_url)
    except:
        return ObjectContainer(header="Sorry!", message="No video available in this category.")

    # This gets the items from the sections on the main video page
    if id:
        item_list = content.xpath('//div[@id="%s"]//li[(@data-type="videos" or @type="videos")]' % (id))

    # This gets the items for any other video page
    else:
        item_list = content.xpath('//ul/li[@data-itemtype="http://schema.org/VideoObject"]')

    for item in item_list:

        link = item.xpath('./meta[@itemprop="url"]/@content')[0]
        if not link.startswith('http://'):
            link = MTV_ROOT + link

        # The itemprop="thumbnail" for some groups gives a default photo, so try img code first
        try:
            image = item.xpath('.//img/@data-original')[0]
        except:
            image = item.xpath('./meta[@itemprop="thumbnail"]/@content')[0]

        if not image.startswith('http://'):
            image = MTV_ROOT + image

        video_title = item.xpath('./meta[@itemprop="name"]/@content')[0].strip()
        summary = item.xpath('./meta[@itemprop="description"]/@content')[0]

        # Get the artist name for videos from artist pages
        if not id:
            artist = title
            video_title = "%s - %s" % (artist, video_title)

        oc.add(VideoClipObject(url=link, title=video_title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        return ObjectContainer(header="Sorry!", message="No video are available in this category.")

    return oc
