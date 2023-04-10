meta:
  id: solar_river_packet
  endian: be

seq:
  - id: magic
    size: 2
  - id: body
    type:
      switch-on: magic
      cases:
        '[0x55, 0xaa]': standard_body
        '[0x02, 0x69]': standard_body
        #_: standard_body

types:
  standard_body:
    seq:
      - id: source_address
        size: 2
      - id: destination_address
        size: 2
      - id: command
        size: 2
      - id: data_payload
        type:
          switch-on: command
          cases:
            '[0x00, 0x00]': data_payload_long
            '[0x00, 0x80]': data_payload_info
            '[0x01, 0x82]': data_payload_pv
            '[0x01, 0x83]': data_payload_inverter_specs
            '[0x01, 0x84]': data_payload_inverter_config
            _: data_payload

  data_payload:
    seq:
      - id: len_data
        type: u1
      - id: data
        size: len_data
      - id: crc
        size: 2

  data_payload_info:
    seq:
      - id: len_data
        type: u1
      - id: data
        size: len_data
      - id: crc
        size: 2

  data_payload_long:
    seq:
      - id: len_data
        type: u1
      - id: data
        size: len_data
      - id: crc
        size: 2
      - id: unknown
        size: 1

  data_payload_pv:
    seq:
      - id: len_data
        type: u1
      - id: data
        type: pv_data
        size: len_data
      - id: crc
        size: 2

  data_payload_inverter_specs:
    seq:
      - id: len_data
        type: u1
      - id: data
        type: specs_data
        size: len_data
      - id: crc
        size: 2

  specs_data:
    seq:
      - id: type
        type: str
        encoding: ascii
        size: 3
      - id: va_rating
        type: str
        encoding: ascii
        size: 4
      - id: firmware
        type: str
        encoding: ascii
        size: 5
      - id: model
        type: str
        encoding: ascii
        size: 16
      - id: manufacturer
        type: str
        encoding: ascii
        size: 16
      - id: serial
        type: str
        encoding: ascii
        size: 16
      - id: unknown
        type: str
        encoding: ascii
        size-eos: true

  data_payload_inverter_config:
    seq:
      - id: len_data
        type: u1
      - id: data
        type: config_data
        size: len_data
      - id: crc
        size: 2

  config_data:
    seq:
      - id: startup_voltage
        type: u2
      - id: time_to_connected_grid
        type: u2
      - id: min_grid_voltage
        type: u2
      - id: max_grid_voltage
        type: u2
      - id: min_grid_frequency
        type: u2
      - id: max_grid_frequency
        type: u2

  pv_data:
    seq:
      - id: internal_temperature
        type: u2
      - id: p1_voltage
        type: u2
      - id: p1_current
        type: u2
      - id: working_hours_high
        type: u2
      - id: working_hours_low
        type: u2
      - id: operating_mode
        type: u1
      - id: unknown1
        type: u1
      - id: total_kwh_today
        type: u2
      - id: unknown2 # potentially fault data
        size: 10
      - id: grid_current
        type: u2
      - id: grid_voltage
        type: u2
      - id: grid_frequency
        type: u2
      - id: output_power
        type: u2
      - id: total_lifetime_kwh_high
        type: u2
      - id: total_lifetime_kwh_low
        type: u2
      - id: rest
        size-eos: true
