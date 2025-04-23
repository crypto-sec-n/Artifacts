import sys, os, base64
from Crypto.Util.Padding import pad
sys.path.append(os.path.join(os.path.dirname(__file__), './python-nostr/'))
from nostr.key import PrivateKey, PublicKey

pk_str = 'nsec...'
pk = PrivateKey.from_nsec(pk_str)
pub_key_recipient = PublicKey.from_npub('npub1ynert69p79kulwzujknnsllsvxp9rxquw3y2sjsgakq935etf4ksrj7sm4').hex()

ciphertext = 'KgnMv948MI6y0bXqqx9751O/VKUhC8TnyUcNh3uPzgK9jHSL8s/ZUiIBnwCKXrIFLYahj+15Bet0dX9w6yeQiDtJwckt5JCF3+BpUWmyuJqXs2FLgt4B5oWHpXBiuhn7KeZvCZELQGZCYbOQ7TUuvlgFzaZZxrWhGrBdgIhDz1c=?iv=roG7VPsiIjv8aPfq/yqt1A=='
#ciphertext = base64.b64decode(ciphertext)
print(len(ciphertext))
#iv = ciphertext[16:32]
#ciphertext = ciphertext[32:48]
#ciphertext = base64.b64encode(ciphertext).decode('utf-8')+"?iv="+base64.b64encode(iv).decode('utf-8')

plaintext = pk.decrypt_message(encoded_message=ciphertext, public_key_hex=pub_key_recipient)
print(plaintext)
a = plaintext.encode('utf-8')
print(a)
print(a.hex())
print(a[32:48].decode('utf-8'))