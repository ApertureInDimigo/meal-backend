from werkzeug.contrib.cache import SimpleCache
cache = {
    "views" : {
        "will" : SimpleCache(),
        "did" : SimpleCache()
    }
}