# tilt2db
Reads from [Tilt Hydrometer](https://tilthydrometer.com/) and writes results to a database

## Why?
The Android app for the Tilt Hydrometer requires a device is always on and in BLE range to read the data and forward it on to a service or a logger. I already have a Raspberry Pi near my fermentation fridge and wanted to leverage that to get the data and move it along. There is the [TiltPi](https://github.com/baronbrew/TILTpi), but I'm not a huge fan of Node Red and found it to lose the connection every so often requiring the service to be restarted. Building on the aioblescan library modifications from `baronbrew`, it didn't look too hard to read the data and push them to a database. My ultimate goal is to pair this with [tilt2bf](https://github.com/mjlocat/tilt2bf) to publish the data to [Brewer's Friend](https://www.brewersfriend.com/) to track the fermentation process.

## Prerequisites
* Tilt Hydrometer
* Linux machine with BLE capabilities (Raspberry Pi 3B or 4 work nicely)
* Python3
* A MySQL or MariaDB database

## Installation
1. Clone the repository

    `git clone https://github.com/mjlocat/tilt2db.git && cd tilt2db`
1. Install the python libraries

    `pip3 install -r requirements.txt`
1. Set up the database

    ``` sql
    CREATE DATABASE tilt;
    CREATE USER tilt IDENTIFIED BY 'mypassword';
    GRANT ALL PRIVILEGES ON tilt.* TO tilt@'%';
    ```
    ``` sh
    # If using a database on the same machine
    mysql -u tilt -p tilt < create_table.sql

    # if using a database on another machine
    mysql -h dbhostname -u tilt -p tilt < create_table.sql
    ```
1. Copy `config.yaml.sample` to `config.yaml` and update the database credentials and calibration settings (see [Calibration](#calibration))

## Usage
Invoke using `python3 tilt2db.py` (If `python` is version 3, you can use that)
```
usage: tilt2db.py [-h] [-c CONFIG] (-s | -t TIME)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Location of the configuration file
  -s, --single          Get one reading then exit
  -t TIME, --time TIME  Minimum time between stored readings in seconds
```

| Command Options | Description |
| --------------- | ----------- |
| `-c CONFIG, --config CONFIG` | Specify the location of the `config.yaml` file |
| `-s, --single` | Get one reading, then exit, useful if running in a cronjob. Either this option or `-t` must be specified |
| `-t TIME, --time TIME` | Wait `TIME` seconds between readings. Either this option or `-s` must be specified |

## Calibration
Fill a large bowl with water and place the Tilt Hydrometer in it. Take the temperature of the water. The temperature reading shown should match the temperature of the water and the Specific Gravity reading should be `1.000`. Adjust the `temp_correction` or `sg_correction` values in `config.yaml` to offset the values. For example:
``` yaml
temp_correction: 1 # Add one degree to the reading
sg_correction: -0.003 # Subtract 3 thousandths from the reading
```
*NOTE*: In this early stage, I'm assuming the offsets are linear. The [Fermentrack documentation](https://docs.fermentrack.com/en/master/gravitysensors/tilt.html#guided-calibration) leads me to believe it may be non-linear.
 