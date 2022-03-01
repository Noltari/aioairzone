# aioairzone
Python library to control Airzone devices.

## Requirements
- Python >= 3.8

## Install
```bash
pip install aioairzone
```

## Install from Source
Run the following command inside this folder
```bash
pip install --upgrade .
```

## Examples
Examples can be found in the `examples` folder

## API Call example
Run the following command to list all your Airzone systems and zones
```
curl --location --request POST "http://192.168.1.25:3000/api/v1/hvac" -d '{"systemID": 0, "zoneID": 0}' | jq
```
