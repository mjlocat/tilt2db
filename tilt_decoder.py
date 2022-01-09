#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# This file from https://github.com/baronbrew/aioblescan/blob/master/aioblescan/plugins/tilt.py and under the MIT license
# The MIT License (MIT)

# Copyright © 2017 Noah Baron

# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# oftware and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT ORxi
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# This file deals with the Tilt formatted message
from struct import unpack
import json
import aioblescan as aios
#Tilt format based on iBeacon format and filter includes Apple iBeacon identifier portion (4c000215) as well as Tilt specific uuid preamble (a495)
TILT = '4c000215a495'


class Tilt(object):
    """
    Class defining the content of a Tilt advertisement
    """

    def decode(self, packet):
        data = {}
        raw_data = packet.retrieve('Payload for mfg_specific_data')
        if raw_data:
            pckt = raw_data[0].val
            payload = raw_data[0].val.hex()
            mfg_id = payload[0:12]
            rssi = packet.retrieve('rssi')
            mac = packet.retrieve("peer")
            if mfg_id == TILT:
                data['uuid'] = payload[8:40]
                data['major'] = unpack('>H', pckt[20:22])[0] #temperature in degrees F
                data['minor'] = unpack('>H', pckt[22:24])[0] #specific gravity x1000
                data['tx_power'] = unpack('>b', pckt[24:25])[0] #weeks since battery change (0-152 when converted to unsigned 8 bit integer) and other TBD operation codes
                data['rssi'] = rssi[-1].val
                data['mac'] = mac[-1].val
                return data