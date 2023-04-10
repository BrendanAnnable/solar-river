# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class SolarRiverPacket(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(2)
        _on = self.magic
        if _on == b"\x55\xAA":
            self.body = SolarRiverPacket.StandardBody(self._io, self, self._root)
        elif _on == b"\x02\x69":
            self.body = SolarRiverPacket.StandardBody(self._io, self, self._root)

    class PvData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.internal_temperature = self._io.read_u2be()
            self.p1_voltage = self._io.read_u2be()
            self.p1_current = self._io.read_u2be()
            self.working_hours_high = self._io.read_u2be()
            self.working_hours_low = self._io.read_u2be()
            self.operating_mode = self._io.read_u1()
            self.unknown1 = self._io.read_u1()
            self.total_kwh_today = self._io.read_u2be()
            self.unknown2 = self._io.read_bytes(10)
            self.grid_current = self._io.read_u2be()
            self.grid_voltage = self._io.read_u2be()
            self.grid_frequency = self._io.read_u2be()
            self.output_power = self._io.read_u2be()
            self.total_lifetime_kwh_high = self._io.read_u2be()
            self.total_lifetime_kwh_low = self._io.read_u2be()
            self.rest = self._io.read_bytes_full()


    class StandardBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.source_address = self._io.read_bytes(2)
            self.destination_address = self._io.read_bytes(2)
            self.command = self._io.read_bytes(2)
            _on = self.command
            if _on == b"\x01\x83":
                self.data_payload = SolarRiverPacket.DataPayloadInverterSpecs(self._io, self, self._root)
            elif _on == b"\x00\x80":
                self.data_payload = SolarRiverPacket.DataPayloadInfo(self._io, self, self._root)
            elif _on == b"\x01\x84":
                self.data_payload = SolarRiverPacket.DataPayloadInverterConfig(self._io, self, self._root)
            elif _on == b"\x00\x00":
                self.data_payload = SolarRiverPacket.DataPayloadLong(self._io, self, self._root)
            elif _on == b"\x01\x82":
                self.data_payload = SolarRiverPacket.DataPayloadPv(self._io, self, self._root)
            else:
                self.data_payload = SolarRiverPacket.DataPayload(self._io, self, self._root)


    class DataPayloadLong(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self.data = self._io.read_bytes(self.len_data)
            self.crc = self._io.read_bytes(2)
            self.unknown = self._io.read_bytes(1)


    class ConfigData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.startup_voltage = self._io.read_u2be()
            self.time_to_connected_grid = self._io.read_u2be()
            self.min_grid_voltage = self._io.read_u2be()
            self.max_grid_voltage = self._io.read_u2be()
            self.min_grid_frequency = self._io.read_u2be()
            self.max_grid_frequency = self._io.read_u2be()


    class DataPayloadInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self.data = self._io.read_bytes(self.len_data)
            self.crc = self._io.read_bytes(2)


    class DataPayloadInverterConfig(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self._raw_data = self._io.read_bytes(self.len_data)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = SolarRiverPacket.ConfigData(_io__raw_data, self, self._root)
            self.crc = self._io.read_bytes(2)


    class SpecsData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = (self._io.read_bytes(3)).decode(u"ascii")
            self.va_rating = (self._io.read_bytes(4)).decode(u"ascii")
            self.firmware = (self._io.read_bytes(5)).decode(u"ascii")
            self.model = (self._io.read_bytes(16)).decode(u"ascii")
            self.manufacturer = (self._io.read_bytes(16)).decode(u"ascii")
            self.serial = (self._io.read_bytes(16)).decode(u"ascii")
            self.unknown = (self._io.read_bytes_full()).decode(u"ascii")


    class DataPayloadPv(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self._raw_data = self._io.read_bytes(self.len_data)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = SolarRiverPacket.PvData(_io__raw_data, self, self._root)
            self.crc = self._io.read_bytes(2)


    class DataPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self.data = self._io.read_bytes(self.len_data)
            self.crc = self._io.read_bytes(2)


    class DataPayloadInverterSpecs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u1()
            self._raw_data = self._io.read_bytes(self.len_data)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = SolarRiverPacket.SpecsData(_io__raw_data, self, self._root)
            self.crc = self._io.read_bytes(2)



