# How to setup environment

## Custom domain settings

See: common-setup.md

## start server

```
cd /path/to/nostream
git checkout sp24-server-for-malicious-client-poc
docker-compose build --no-cache
docker-compose up
```

## launch attcker environment

- Install Node v16.x
- Install npm and yarn
- Install Python3.x ( recommended version is Python3.9)

### make a malicious QR code for attack and display it

```
cd attacker-web-app/connect/example/
yarn install
yarn start
# then access to http://localhost:1234/ via the Browser on your PC
```

### launch attacker's server to get plaintext-ciphertext pair

```
cd attacker-server/catch_event_from_connect
pip3 tornado secp256k1 cryptography pycryptodome websocket-client
python3 poc.py
```

## Prepare for Client

### Install nostrum on your device

#### For iOS

##### Option1: Join TestFlight

Join TestFlight. See https://github.com/nostr-connect/nostrum/blob/master/README.md

##### Option2: install via Expo Go

- 1. Install Expo on your iOS device https://apps.apple.com/jp/app/expo-go/id982107779
- 2. Run following command

```
git clone https://github.com/nostr-connect/nostrum.git
cd nostrum
yarn install
yarn start
# Launch App and QR code will be shown
```

- 3. Read QR code on your terminal using iOS native Camera app
- 4. Launch Nostrum via Expo Go

#### For Android

- 1. Download APK file from https://github.com/nostr-connect/nostrum/blob/master/README.md
- 2. Install APK file on your Android device

### Launch nostrum and sign-in

- 1. Launch nostrum
- 2. Sign-in nostrum using your nostr private key that same as you're using on your nostr client app.
- 3. Read Malicious QR via your Camera on http://localhost:1234/ 
- 4. Push Accept button on your screen.
- 5. Our attack will works.

