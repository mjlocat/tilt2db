CREATE TABLE tilt_readings (
  id BIGINT NOT NULL AUTO_INCREMENT,
  color VARCHAR(6) NOT NULL,
  temperature INTEGER NOT NULL,
  sg FLOAT NOT NULL,
  tx_power INTEGER,
  rssi INTEGER,
  mac CHAR(17) NOT NULL,
  insert_dttm TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
);
