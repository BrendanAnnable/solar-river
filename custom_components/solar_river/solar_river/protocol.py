import asyncio
import logging
import async_timeout
from enum import Enum

from .solar_river_packet import SolarRiverPacket

from .abstract import Samil, SamilInverter
from .model import (
    InverterConfig,
    InverterPVData,
    InverterSpecs,
)

MAGIC_HEADER = b"\x55\xaa"

_LOGGER = logging.getLogger(__name__)


class Command(Enum):
    RESET_NETWORK = b"\x00\x04"
    REQUEST_SERIAL = b"\x00\x00"
    REQUEST_ADDRESS = b"\x00\x01"

    REQUEST_PV_DATA = b"\x01\x02"
    REQUEST_SPECIFICATIONS = b"\x01\x03"
    REQUEST_CONFIGURATION = b"\x01\x04"


class SolarRiverCodec:
    @staticmethod
    def encode(command: Command, src=b"\x00\x00", dst=b"\x00\x00", data=b"") -> bytes:
        length = len(data)
        packet = b"".join(
            [MAGIC_HEADER, src, dst, command.value, length.to_bytes(1, "big"), data]
        )
        crc = sum(packet).to_bytes(2, "big")
        return packet + crc

    @staticmethod
    def decode(packet: bytes) -> SolarRiverPacket:
        return SolarRiverPacket.from_bytes(packet)

    @staticmethod
    def decode_specs(specs: SolarRiverPacket.SpecsData) -> InverterSpecs:
        return InverterSpecs(
            int(specs.type.strip()),
            specs.va_rating.strip(),
            specs.firmware.strip(),
            specs.model.strip(),
            specs.manufacturer.strip(),
            specs.serial.strip(),
        )

    @staticmethod
    def decode_config(config: SolarRiverPacket.ConfigData) -> InverterConfig:
        return InverterConfig(
            config.startup_voltage / 10,
            config.time_to_connected_grid,
            config.min_grid_voltage / 10,
            config.max_grid_voltage / 10,
            config.min_grid_frequency / 100,
            config.max_grid_frequency / 100,
        )

    @staticmethod
    def decode_pv_data(pv_data: SolarRiverPacket.PvData) -> InverterPVData:
        return InverterPVData(
            pv_data.internal_temperature / 10,
            pv_data.p1_voltage / 10,
            pv_data.p1_current / 10,
            (pv_data.working_hours_high << 16) + pv_data.working_hours_low,
            pv_data.operating_mode,
            pv_data.total_kwh_today / 100,
            pv_data.grid_current / 10,
            pv_data.grid_voltage / 10,
            pv_data.grid_frequency / 100,
            pv_data.output_power,
            ((pv_data.total_lifetime_kwh_high << 16) + pv_data.total_lifetime_kwh_low) / 10,
        )


class SolarRiverIO:
    def __init__(self, host: str, port: int, timeout=2):
        self.host = host
        self.port = port
        self.connection = None
        self.sem = asyncio.Semaphore()
        self.timeout = timeout

    async def get_connection(self, retry=2) -> (asyncio.StreamReader, asyncio.StreamWriter):
        for i in range(retry + 1):
            try:
                if not self.connection:
                    async with async_timeout.timeout(self.timeout):
                        self.connection = await asyncio.open_connection(self.host, self.port)
                return self.connection
            except TimeoutError as ex:
                _LOGGER.exception(f'Connection Timeout, retrying...{i + 1} of {retry}', exc_info=ex)
                await asyncio.sleep(1)
            except ConnectionError as ex:
                _LOGGER.exception(f'Connection Error retrying...{i + 1} of {retry}', exc_info=ex)
                await asyncio.sleep(1)
        raise ConnectionError

    async def write_packet(self, packet) -> None:
        (_, writer) = await self.get_connection()
        writer.write(packet)
        await writer.drain()

    async def read_packet(self) -> bytes:
        (reader, _) = await self.get_connection()
        header = await reader.readexactly(9)
        data_len = header[8]
        data_and_crc = await reader.readexactly(data_len + 2)
        buffer = header + data_and_crc
        # print("res", buffer)
        # print()
        return buffer

    async def send_command(self, packet) -> bytes:
        for i in range(3):
            try:
                async with async_timeout.timeout(self.timeout):
                    return await self._send_command(packet)
            except TimeoutError as ex:
                _LOGGER.exception('Timeout', exc_info=ex)
            except ConnectionError as ex:
                _LOGGER.exception('Connection Error', exc_info=ex)
                self.connection = None
        _LOGGER.error(f'Failed to send command {packet}')
        raise ConnectionError

    async def _send_command(self, packet) -> bytes:
        async with self.sem:
            await self.write_packet(packet)
            packet = await self.read_packet()
            await asyncio.sleep(0.2)
            return packet


class InverterRouter:
    def __init__(self, io: SolarRiverIO):
        self.io = io
        self.routing_table = dict()

    async def find_inverters(self, search_time_secs=10, time_between_attempts_secs=0.5) -> list[bytes]:
        async with async_timeout.timeout(search_time_secs * 2):
            _LOGGER.info('RESET_NETWORK REQ')
            await self.io.write_packet(SolarRiverCodec.encode(command=Command.RESET_NETWORK))

            # Here we mimic the official SolarPower Browser software by repeatedly polling for serial numbers.
            serials = set()
            for i in range(int(search_time_secs / time_between_attempts_secs)):
                try:
                    async with async_timeout.timeout(time_between_attempts_secs):
                        _LOGGER.info('REQUEST_SERIAL REQ')
                        await self.io.write_packet(SolarRiverCodec.encode(command=Command.REQUEST_SERIAL))
                        packet = await self.io.read_packet()
                        serial = SolarRiverCodec.decode(packet).body.data_payload.data
                        serials.add(serial)
                        _LOGGER.info('REQUEST_SERIAL RES', serial)
                        # Inverter responds with two packets, it is currently unknown what this second packet describes.
                        await self.io.read_packet()
                    await asyncio.sleep(time_between_attempts_secs)
                except TimeoutError as ex:
                    _LOGGER.exception('No reply', exc_info=ex)

            return list(serials)

    async def get_inverter_address(self, serial: bytes) -> bytes:
        try:
            return self.routing_table[serial]
        except KeyError:
            packet = await self.io.send_command(
                SolarRiverCodec.encode(command=Command.REQUEST_ADDRESS, data=serial)
            )
            address = SolarRiverCodec.decode(packet).body.source_address
            self.routing_table[serial] = address
            # await asyncio.sleep(0.1)  # Inverter won't respond immediately to this address, sleep momentarily.
            return address

    async def send_command(self, serial: bytes, command: Command) -> SolarRiverPacket.DataPayload:
        for i in range(3):
            try:
                async with async_timeout.timeout(2):
                    return await self._send_command(serial, command)
            except TimeoutError:
                pass
            except ConnectionError:
                # Assume the worst and clear routing the table on any connection error.
                self.routing_table.clear()
        raise ConnectionError

    async def _send_command(self, serial: bytes, command: Command) -> SolarRiverPacket.DataPayload:
        address = await self.get_inverter_address(serial)
        _LOGGER.info('addr', address)
        req = SolarRiverCodec.encode(command=command, dst=address)
        _LOGGER.info('req', req)
        res = await self.io.send_command(req)
        _LOGGER.info('res', res)
        return SolarRiverCodec.decode(res).body.data_payload.data



class SamilInverterImpl(SamilInverter):
    def __init__(self, serial: bytes, router: InverterRouter):
        self.serial = serial
        self.router = router

    async def get_specs(self) -> InverterSpecs:
        return SolarRiverCodec.decode_specs(
            await self.router.send_command(self.serial, Command.REQUEST_SPECIFICATIONS)
        )

    async def get_config(self) -> InverterConfig:
        return SolarRiverCodec.decode_config(
            await self.router.send_command(self.serial, Command.REQUEST_CONFIGURATION)
        )

    async def get_pv_data(self) -> InverterPVData:
        return SolarRiverCodec.decode_pv_data(
            await self.router.send_command(self.serial, Command.REQUEST_PV_DATA)
        )


class SamilImpl(Samil):
    def __init__(self, inverters):
        self.inverters = inverters

    @staticmethod
    async def discover_inverters(host: str, port: int) -> Samil:
        io = SolarRiverIO(host, port)
        router = InverterRouter(io)
        serials = await router.find_inverters()
        inverters = []
        for serial in serials:
            inverters.append(SamilInverterImpl(serial, router))
        return SamilImpl(inverters)
