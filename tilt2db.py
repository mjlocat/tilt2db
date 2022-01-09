import os
import sys
import argparse
from datetime import datetime
import aioblescan
import asyncio
import yaml
from mysql import connector as myc
from tilt_decoder import Tilt

class DB:
  def __init__(self, config):
    self.dbconfig = config['db']
    

  def save_values(self, uuid, temperature, sg, tx_power, rssi, mac):
    insert = "insert into tilt_readings (uuid, temperature, sg, tx_power, rssi, mac, insert_dttm) values (%s, %s, %s, %s, %s, %s, %s)"
    cnx = myc.connect(**self.dbconfig)
    cursor = cnx.cursor()
    cursor.execute(insert, (uuid, temperature, sg, tx_power, rssi, mac, datetime.now()))
    cnx.commit()
    cursor.close()
    cnx.close()


class TILTReader:
  def __init__(self, args):
    self.args = args
    configfile = 'config.yaml'
    if args.config is not None:
      configfile = args.config
    self.config = yaml.safe_load(open(configfile, 'r'))
    self.db = DB(self.config)
    self.lastreading = datetime.min
    self.run_event_loop()


  def ble_reader(self, data):
    if self.args.time is not None:
      now = datetime.now()
      duration = now - self.lastreading
      if duration.total_seconds() < self.args.time:
        return

    el = asyncio.get_running_loop()
    event = aioblescan.HCI_Event()
    event.decode(data)
    reading = Tilt().decode(event)
    if reading:
      temp_correction = 0
      sg_correction = 0
      if 'temp_correction' in self.config.keys():
        temp_correction = int(self.config['temp_correction'])

      if 'sg_correction' in self.config.keys():
        sg_correction = float(self.config['sg_correction'])

      temperature = reading['major'] + temp_correction
      sg = (reading['minor'] / 1000) + sg_correction
      self.db.save_values(reading['uuid'], temperature, sg, reading['tx_power'], reading['rssi'], reading['mac'])
      if self.args.single:
        el.stop()
      else:
        self.lastreading = datetime.now()



  def run_event_loop(self):
    el = asyncio.get_event_loop()
    sock = aioblescan.create_bt_socket(0)
    factory = el._create_connection_transport(sock, aioblescan.BLEScanRequester, None, None)
    conn,btctrl = el.run_until_complete(factory)
    btctrl.process = self.ble_reader
    btctrl.send_scan_request()
    try:
      el.run_forever()

    finally:
      btctrl.stop_scan_request()
      cmd = aioblescan.HCI_Cmd_LE_Advertise(enable=False)
      btctrl.send_command(cmd)
      conn.close()
      el.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', help="Location of the configuration file")
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('-s', '--single', help="Get one reading then exit", action="store_true")
  group.add_argument('-t', '--time', help="Minimum time between stored readings in seconds", type=int)
  args = parser.parse_args()
  if os.getuid() != 0:
    sys.stderr.write("Must run as root to scan BLE devices\n")
    sys.exit(-1)

  TILTReader(args)
