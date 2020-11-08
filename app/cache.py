# from werkzeug.contrib.cache import SimpleCache
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})