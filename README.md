# BlueIris Scanner
After encountering a BlueIris camera at work, I decided to poke around and see what information was publicly available just by reading through their documentation ([found here](https://blueirissoftware.com/BlueIris.PDF)). I eventually wrote this scanner in Python, which will run through all possible commands through the camera's JSON interface. If anonymous access is enabled (no login required), it will enumerate information such as camera names, CPU and memory stats, last software update, uptime, and more. 

## Installation
```bash
git clone https://github.com/Legoclones/blueiris-scanner
cd blueiris-scanner
pip3 install requests
```

## Run
```bash
python3 blueiris_scanner.py -H https://link.to.camera [-u userfile.txt] [-p passwordfile.txt] [-v]
```

If a userfile and password file are passed in, the scanner will also brute force credentials. If either of those files aren't passed it, the credentials won't be brute forced.

## Disclaimer
I don't intend to maintain this tool or ensure it works for newer versions (it was tested on `BlueServer/4.8.6.3`), however if you'd like to contribute feel free to make a pull request!