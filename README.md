# aioairzone
[![Latest Version][mdversion-button]][md-pypi]
[![Python Versions][pyversion-button]][md-pypi]
[![License: Apache 2.0][apache-button]](LICENSE)

[apache-button]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[md-pypi]: https://pypi.org/project/aioairzone
[mdversion-button]: https://img.shields.io/pypi/v/aioairzone.svg
[pyversion-button]: https://img.shields.io/pypi/pyversions/aioairzone.svg

Python library to control Airzone devices.

## Requirements
- Python >= 3.11

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

## API Call examples
Run the following command to list all your Airzone Zones:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/hvac" -d '{"systemID": 0, "zoneID": 0}' | jq
```

Run the following command to list all your Airzone Systems:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/hvac" -d '{"systemID": 127}' | jq
```

Run the following command to fetch your Airzone Altherma parameters:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/hvac" -d '{"systemID": 0}' | jq
```

Run the following command to fetch your Airzone WebServer parameters:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/webserver" | jq
```

Run the following command to fetch a demo Airzone Zone:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/demo" | jq
```

Run the following command to fetch your Airzone LocalAPI version:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/version" | jq
```

Run the following command to fetch your Airzone LocalAPI integration driver:
```
curl -s --location --request POST "http://192.168.1.25:3000/api/v1/integration" -d '{}' | jq
```
