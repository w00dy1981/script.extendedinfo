import xbmcaddon,os,xbmc,xbmcvfs
import simplejson as json
from Utils import *
import urllib
from urllib2 import Request, urlopen

moviedb_key = '34142515d9d23817496eeb4ff1d223d0'      
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def HandleTheMovieDBMovieResult(results):
    base_url,size = GetMovieDBConfig()
    movies = []
    log("starting HandleTheMovieDBMovieResult")
    try:
        for movie in results["results"]:
            newmovie = {'Art(fanart)': base_url + size + movie['backdrop_path'],
                        'Art(poster)': base_url + size + movie['poster_path'],
                        'Title': movie['title'],
                        'OriginalTitle': movie['original_title'],
                        'ID': movie['id'],
                        'Rating': movie['vote_average'],
                        'ReleaseDate':movie['release_date']  }
            movies.append(newmovie)
    except Exception, e:
        log(e)
        log("Error when handling TheMovieDB movie results")
    return movies
    
def HandleTheMovieDBListResult(results):
    base_url,size = GetMovieDBConfig()
    lists = []
    log("starting HandleTheMovieDBListResult")
    try:
        for list in results["results"]:
            newlist = {'Art(poster)': base_url + size + list['poster_path'],
                        'Title': list['name'],
                        'ID': list['id'],
                        'Description': list['description']}
            lists.append(newlist)
    except:
        pass
    return lists
    
def HandleTheMovieDBPeopleResult(results):
    people = []
    log("starting HandleLastFMPeopleResult")
    try:
        for person in results:
            newperson = {'adult': person['adult'],
                        'name': person['name'],
                        'also_known_as': person['also_known_as'],
                        'biography': person['biography'],
                        'birthday': person['birthday'],
                        'id': person['id'],
                        'deathday': person['deathday'],
                        'place_of_birth': person['place_of_birth'],
                        'thumb': person['profile_path']  }
            people.append(newperson)
    except:
        log("Error when handling TheMovieDB people results")
    return people
    
def HandleTheMovieDBCompanyResult(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    try:
        for company in results:
            log(company)
            newcompany = {'parent_company': company['parent_company'],
                        'name': company['name'],
                        'description': company['description'],
                        'headquarters': company['headquarters'],
                        'homepage': company['homepage'],
                        'id': company['id'],
                        'logo_path': company['logo_path'] }
            companies.append(newcompany)
    except:
        log("Error when handling TheMovieDB companies results")
    return companies
    
def SearchforCompany(Company):
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/search/company?query=%s&api_key=%s" % (urllib.quote_plus(Company),moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    if len(response["results"]) > 0:
        return response["results"][0]["id"]
    else:
        return ""
    
def GetMovieDBConfig():
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/configuration?api_key=%s" % (moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    save_to_file(response,"MovieDBConfig",Addon_Data_Path)
    log("MovieDB Config")
    log(response["images"]["base_url"])
    return (response["images"]["base_url"],response["images"]["poster_sizes"][-1])
    
def GetCompanyInfo(Id):
    try:
        headers = {"Accept": "application/json"}
        request = Request("http://api.themoviedb.org/3/company/%s/movies?append_to_response=movies&api_key=%s" % (Id,moviedb_key), headers=headers)
        response = urlopen(request).read()
        response = json.loads(response)
        log("Company response:")
        log(response)
        return HandleTheMovieDBMovieResult(response)
    except:
        return []
    
def GetExtendedMovieInfo(Id):
    base_url,size = GetMovieDBConfig()
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/movie/%s?append_to_response=trailers,casts&api_key=%s" % (Id,moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    prettyprint(response)
    log("GetExtendedMovieInfo response:")
    log(response)
    if 1 == 1:
        authors = []
        directors = []
        genres = []
        for item in response['genres']:
            genres.append(item["name"])
        for item in response['casts']['crew']:
            log(item)
            if item["job"] == "Author":
                authors.append(item["name"])
            if item["job"] == "Director":
                directors.append(item["name"])
        Writer = " / ".join(authors)
        Director = " / ".join(directors)
        Genre = " / ".join(genres)
        if len(response['trailers']['youtube']) > 0:
            Trailer = response['trailers']['youtube'][0]['source']
        else:
            Trailer = ""
        if len(response['production_countries']) > 0:
            Country = response['production_countries'][0]["name"]
        else:
            Country = ""
        if len(response['production_companies']) > 0:
            Studio = response['production_companies'][0]["name"]
        else:
            Studio = ""
        newmovie = {'Art(fanart)': base_url + size + response['backdrop_path'],
                    'Fanart': base_url + size + response['backdrop_path'],
                    'Art(poster)': base_url + size + response['poster_path'],
                    'Poster': base_url + size + response['poster_path'],
                    'Title': response['title'],
                    'Label': response['title'],
                    'Tagline': response['tagline'],
                    'RunningTime': response['runtime'],
                    'Budget': response['budget'],
                    'Director': Director,
                    'Writer': Writer,
                    'Budget': response['budget'],
                    'Homepage': response['homepage'],
                    'Set': response['belongs_to_collection'],
                    'ID': response['id'],
                    'Plot': response['overview'],
                    'OriginalTitle': response['original_title'],
                    'Genre': Genre,
                    'ID': response['id'],
                    'Rating': response['vote_average'],
                    'Play': 'PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid=%s)' %Trailer,
                    'Trailer': 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' %Trailer,
                    'ReleaseDate':response['release_date'],
                    'Country':Country,
                    'Studio':Studio,
                    'Year':response['release_date'][:4]  }
    else:
        return False
    return newmovie
     
def GetMovieLists(Id):
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/movie/%s/lists?append_to_response=movies&api_key=%s" % (Id,moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    log(response)
    return HandleTheMovieDBListResult(response)
    
def GetSimilarMovies(Id):
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/movie/%s/similar_movies?append_to_response=translations,releases,trailers&api_key=%s" % (Id,moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    log("in GetSimilarMovies")
    log(response)
    return HandleTheMovieDBMovieResult(response)        
        
def search_movie(medianame,year = ''):
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame, year) )
    medianame = urllib.quote_plus(medianame.encode('utf8','ignore'))
    headers = {"Accept": "application/json"}
    log(medianame)
    request = Request("http://api.themoviedb.org/3/search/movie?query=%s+%s&api_key=%s" % (medianame, year, moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    tmdb_id = ''
    try:
        if response == "Empty":
            tmdb_id = ''
        else:
            for item in response['results']:
                if item['id']:
                    tmdb_id = item['id']
                    log(tmdb_id)
                    break
    except Exception, e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found ID: %s' %tmdb_id)
    return tmdb_id
        