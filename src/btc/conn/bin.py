from binance import Client  #, ThreadedWebsocketManager, ThreadedDepthCacheManager
from dynaconf import settings
client = Client(settings.binance.api_key, settings.binance.api_secret)
