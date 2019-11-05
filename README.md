# dmzj-DB
This repo aim to preserve dmzj's contents info.

DMZJ is now hiding mangas from users in their v3 api, yet v2 api still works. In this project, python script is used to fetch manga infos from v3 api first, then v2 api if failed. All fetched data is now stored in protobuff.

The information includes mangaID, and chapterID. With this two, a chapter API call could provide address to images, format provided below. 

# APIs
v2: `http://v2.api.dmzj.com/comic/${mangaID}.json`

v3: `http://v3api.dmzj.com/comic/${mangaID}.json`

chapter: `http://m.dmzj.com/chapinfo/${mangaID}/${chapterID}.html`

Android URL scheme: `dmzj://dmzj.com/comic?id=${mangaID}`

Android URL scheme will invoke dmzj app when clicked in android environment, same should work in iOS devices. However, since dmzj app is using the latest(at the moment of writing) v3 API, a blank screen will be returned, as a result of return `"漫画不存在！！！"` from v3 API.

# TODO
1. Add support for light novels.
2. Store data in MariaDB.
3. Constontly use `Recent Updated` API to update database.
4. To compensate for goal 3, a `Next Chapter` API call could in theory get next chapter untill reached the latest.
5. Add NodeJS backend, find a way to open chapter in dmzj app.
