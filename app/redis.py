import redis
from config import REDIS_URL
import datetime, time
rd = redis.Redis().from_url(url=REDIS_URL)

# r.set('foo', 'bar')
value = rd.get('foo')
print(value)

temp = "pviews:14-b'4'"

print(rd.get(temp))