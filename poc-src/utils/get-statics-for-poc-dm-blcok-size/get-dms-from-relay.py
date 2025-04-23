import sys,os
import statistics
import random,string,json,datetime,pickle, base64
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))

import json
import ssl
import time
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import PrivateKey, PublicKey

# Relay for testing
RELAY = "relay.example.com"

# Relays not working
#RELAY = "nostr.wine"
#RELAY = "nos.land"

# Relays can get dm statics
#RELAY = "relay.damus.io"
#RELAY = "nos.lol"
#RELAY = "yabu.me"


VICTIM_PUBKEY_NPUB = "npub1ynert69p79kulwzujknnsllsvxp9rxquw3y2sjsgakq935etf4ksrj7sm4"
VICTIM_PUBKEY = PublicKey.from_npub(VICTIM_PUBKEY_NPUB).hex()

#filters = Filters([Filter(authors=[VICTIM_PUBKEY], kinds=[EventKind.TEXT_NOTE])])
#filters = Filters([Filter(authors=[VICTIM_PUBKEY], kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE])])
#filters = Filters([Filter(kinds=[EventKind.TEXT_NOTE])])

COLLECTION_NUM = 10000

dm_list_all = list()
until_unix_sec = int(datetime.datetime.now().timestamp())
print('Get Until...')
print(datetime.datetime.fromtimestamp(until_unix_sec))

for _ in range(COLLECTION_NUM//500 + 5):
  filters = Filters([Filter(kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE], limit=500, until=until_unix_sec)])

  subscription_id = "".join(random.choices(string.ascii_lowercase, k=64))
  request = [ClientMessageType.REQUEST, subscription_id]
  request.extend(filters.to_json_array())

  relay_manager = RelayManager()
  relay_manager.add_relay("wss://" + RELAY)
  relay_manager.add_subscription(subscription_id, filters)
  relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
  time.sleep(1.25) # allow the connections to open

  message = json.dumps(request)
  relay_manager.publish_message(message)
  time.sleep(1) # allow the messages to send

  dm_list = list()

  while relay_manager.message_pool.has_events():
    event_msg = relay_manager.message_pool.get_event()
    dm_list.append(json.loads(event_msg.event.to_message())[1])


  relay_manager.close_connections()



  dm_list_all +=dm_list
  
  if len(dm_list_all)>=COLLECTION_NUM:
     break
  print('aaaaa')
  
  dm_list_sorted = sorted(dm_list, key=lambda x:x['created_at'])
  until_unix_sec = dm_list_sorted[0]['created_at']-1
  print('Get Until...')
  print(datetime.datetime.fromtimestamp(until_unix_sec))

  time.sleep(1) # allow the messages to send

#print(ciphertext_length_list)
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)

filename = "dm-%s-%s.pickle" % (RELAY, now.strftime('JST-%y-%m-%d-%H-%M-%S'))
with open(filename, mode="wb") as f:
    pickle.dump(dm_list_all, f)

print('dm_list_all length:%d' % len(dm_list_all))
unique_dm_list = list({dm["id"]: dm for dm in dm_list_all}.values())
print('unique_dm_list length:%d' % len(unique_dm_list))

ciphertext_length_list = list()
for d in unique_dm_list:
    if not 'content' in d:
      continue
    content = d['content'].split('?iv=')
    if len(content)<2:
        continue
    c_b64, iv_b64 = content
    c = base64.b64decode(c_b64)
    ciphertext_length_list.append(len(c))
  


print('Collected DMs:%d' % len(ciphertext_length_list))
print('Max:%d' % max(ciphertext_length_list))
print('Min:%d' % min(ciphertext_length_list))
print('Avg:%d' % (sum(ciphertext_length_list)/len(ciphertext_length_list)))
print('Median:%d' % statistics.median(ciphertext_length_list))
print('Mode:%s' % (" and ".join([str(i) for i in statistics.multimode(ciphertext_length_list)])))



'''
# How to load ( as dict )
with open('dm-JST-23-12-05-14-30-49.pickle', 'rb') as f:
   import pickle
   a = pickle.load(f)
'''