import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    searchString = encodedTitle.replace(" ","+")
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString)
    for searchResult in searchResults.xpath('//div[contains(@class,"compact")]//article'):
        titleNoFormatting = searchResult.xpath('.//a//h3')[0].text_content()
        curID = searchResult.xpath('.//a')[0].get('href')
        curID = curID.replace('/','_').replace('?','!')
        releaseDate = parse(searchResult.xpath('.//div[@class="date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        searchString = searchString.replace("+"," ")
        if searchDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [" + PAsearchSites.getSearchSiteName(siteNum) + "] " + releaseDate, score = score, lang = lang))

    return results
def update(metadata,siteID,movieGenres,movieActors):
    url = PAsearchSites.getSearchBaseURL(siteID) + str(metadata.id).split("|")[0].replace('_','/').replace('!','?')
    Log("scene url: " + url)
    detailsPageElements = HTML.ElementFromURL(url)

    # Studio/Tagline/Collection
    metadata.studio = PAsearchSites.getSearchSiteName(siteID)
    metadata.tagline = metadata.studio
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Date
    date = detailsPageElements.xpath('//p[@class="meta"]//span')[0].text_content().strip()
    Log('date: ' + date)
    date_object = datetime.strptime(date.strip(), '%d %b, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="desc"]')[0].text_content()
    Log('summary: ' +  metadata.summary)

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    posters = detailsPageElements.xpath('//div[@class="swiper-slide"]//img')
    background = posters[0].get("src").replace('medium','large')
    Log("background: " + background)
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
# unneccesary binocular pictures - non-functional as written
    # posterNum = 1
    # for posterCur in posters:
    #     posterURL = posterCur.get("src")
    #     Log("posterURL: " + posterURL)
    #     metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
    #     posterNum = posterNum + 1

    # Actors / poster
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//p[@class="meta"]//span[3]//a')
    if len(actors) > 0:
        posterNum = 2
        for actorLink in actors:
            actorName = actorLink.text_content()
            actorPageURL = PAsearchSites.getSearchBaseURL(siteID) + actorLink.get("href")
            Log(actorName + ": " + actorPageURL)
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorPhotoURL = actorPage.xpath('//div[@class="actor"]//img')[0].get("src")
            Log('actorPhotoURL: ' + actorPhotoURL)
            movieActors.addActor(actorName,actorPhotoURL)
            # Actor profile pic as possible poster
            metadata.posters[actorPhotoURL] = Proxy.Preview(HTTP.Request(actorPhotoURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
            posterNum += 1

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('.//p[@class="meta"]//span[@class="clear"]//a')
    if len(genres) > 0:
        for genre in genres:
            movieGenres.addGenre(genre.text_content())

    # TITLE

    title = detailsPageElements.xpath('//div[contains(@class,"title")]//h2')[0].text_content()
    metadata.title = metadata.studio + " - " + title


    return metadata
