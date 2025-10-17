# pyMatis

[![License](https://img.shields.io/github/license/scabrero/pymatis)](https://img.shields.io/github/license/scabrero/pymatis)
[![PyPI version](https://badge.fury.io/py/pymatis.svg)](https://badge.fury.io/py/pymatis)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymatis)](https://img.shields.io/pypi/pyversions/pymatis)

A Python library to interface with Matismart IoT electrical devices.

## Description

[Shanghai Matis Electric Co., Ltd. (MATIS)](https://www.matismart.com/) offers smart AIoT electrical solutions, including hardware and software. Their product line includes smart power monitoring, energy meters, circuit breakers and reclosers.

## Supported devices

This library supports and has been tested with the following devices:

### Auto-Reclosers

* [MT53RAsx](https://www.matismart.com/product/auto-recloser-mt53.htm)

## Installation

```bash
python -m pip install pymatis
```

## How to use

The library offers a high level and easy to use API:

```
transport = MatisModbusRTUTransport(device="/dev/ttyACM0")
api = MT53RAsx(transport)
```

A command line interface is also included in the library for testing purposes. Use the `help` or `?` command to get the list of available commands in each context.
