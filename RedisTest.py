import redis

# Redis configuration
redis_host = "amp-my-7kn4uaxblwzd.6xkwqy.0001.aps1.cache.amazonaws.com"
redis_port = int(6379)

# Connect to Redis
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# Example: List all keys
all_keys = redis_client.keys('*')
print("All Keys:", all_keys)