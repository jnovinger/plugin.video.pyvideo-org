import xbmcplugin, xbmcgui, xbmcaddon, urlparse, urllib2, json, sys

CONFERENCES_URL = "http://pyvideo.org/api/v1/category/"
CONFERENCE_URL = "http://pyvideo.org/api/v1/category/{id}/"
VIDEO_URL = "http://pyvideo.org/api/v1/video/{id}/"
NUM_ROWS = 10
 
def addLink(name, url):
    li = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
    li.setProperty("IsPlayable", "true")
    li.setInfo(type="Video", infoLabels={"Title":name})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=li, isFolder=False)
    
def addDir(name,path,page):
    u=sys.argv[0]+"?path=%s&page=%s"%(path,str(page))
    li=xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=li,isFolder=True)

def add_video(video):
  url = None
  domain = None 
  for format in ['video_ogv_url', 'video_webm_url', 'video_mp4_url', 'video_flv_url']:
    if video[format]:
      url = video[format]
 
  if url == None:  
    url = video['source_url']
    if 'youtube' in url:
      v = urlparse.parse_qs(urlparse.urlparse(url).query)['v'][0]
      url = "plugin://plugin.video.youtube?path=/root/video&action=play_video&videoid=%s"%v 
      domain = "www.youtube.com"
    else:
      if url.find(".ogv") == 0 and url.find(".webm") == 0 and url.find(".mp4") == 0 and url.find(".flv") == 0:
        url = None

  if url != None:
    if domain == None:
      domain = urlparse.urlparse(url).netloc
    addLink("%s (%s)"%(video["title"],domain), url)
    
try:
  params = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)
  path = params['path'][0]
  page = int(params['page'][0])
except:
  path = '/'
  page = 1

try:
  if path == '/':
    conferences_string = urllib2.urlopen(CONFERENCES_URL).read()
    conferences = json.loads(conferences_string)
    for conference in conferences['objects']:
      addDir(conference['title'], '/conference/%s'%conference['id'], 1)
        
  elif path.startswith('/conference/'):
    conference_details = path.split('/')
    from_row = (page * NUM_ROWS) - NUM_ROWS + 1
    id = conference_details[2]
    conference_string = urllib2.urlopen(CONFERENCE_URL.format(id=id)).read()
    conference = json.loads(conference_string)
    video_ids = [v.split('/')[-2] for v in conference['videos']]
    videos_length = len(video_ids)
    counter = 0
    for video_id in video_ids:
      counter += 1
      if counter >= from_row:
        url = VIDEO_URL.format(id=video_id)
        video_string = urllib2.urlopen(url).read()
        video = json.loads(video_string)                                                                       
        add_video(video)   
      
      if (counter == (from_row + NUM_ROWS-1)) and (counter < videos_length):  
        addDir("Next Page >>", "/conference/%s"%id,page+1)
        break

  else:
    addDir("ERROR: Path %s not valid"%path, path, 1)
except Exception as e:
  addDir("%s"%e,"",1)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
