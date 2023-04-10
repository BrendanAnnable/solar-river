from dataclasses import dataclass


@dataclass
class InverterSpecs:
    type: int
    va_rating: str
    firmware: str
    model: str
    manufacturer: str
    serial: str


@dataclass
class InverterConfig:
    startup_voltage: float
    time_to_connected_grid: float
    min_grid_voltage: float
    max_grid_voltage: float
    min_grid_frequency: float
    max_grid_frequency: float


@dataclass
class InverterPVData:
    internal_temperature: float
    p1_voltage: float
    p1_current: float
    working_hours: float
    operating_mode: int
    total_kwh_today: float
    grid_current: float
    grid_voltage: float
    grid_frequency: float
    output_power: int
    total_lifetime_kwh: float


class InverterSpecs2:
    def __init__(
        self,
        *,
        type: int,
        va_rating: str,
        firmware: str,
        model: str,
        manufacturer: str,
        serial: str,
    ):
        self.type = type
        self.va_rating = va_rating
        self.firmware = firmware
        self.model = model
        self.manufacturer = manufacturer
        self.serial = serial


class InverterConfig2:
    def __init__(
        self,
        *,
        startup_voltage: int,
        time_to_connected_grid: int,
        min_grid_voltage: int,
        max_grid_voltage: int,
        min_grid_frequency: int,
        max_grid_frequency: int,
    ):
        self.startup_voltage = startup_voltage
        self.time_to_connected_grid = time_to_connected_grid
        self.min_grid_voltage = min_grid_voltage
        self.max_grid_voltage = max_grid_voltage
        self.min_grid_frequency = min_grid_frequency
        self.max_grid_frequency = max_grid_frequency


class InverterPVData2:
    def __init__(
        self,
        *,
        internal_temperature: int,
        p1_voltage: int,
        p1_current: int,
        working_hours_high: int,
        working_hours_low: int,
        operating_mode: int,
        total_kwh_today: int,
        grid_current: int,
        grid_voltage: int,
        grid_frequency: int,
        output_power: int,
        total_lifetime_kwh_high: int,
        total_lifetime_kwh_low: int,
    ):
        self.internal_temperature = internal_temperature
        self.p1_voltage = p1_voltage
        self.p1_current = p1_current
        self.working_hours_high = working_hours_high
        self.working_hours_low = working_hours_low
        self.operating_mode = operating_mode
        self.total_kwh_today = total_kwh_today
        self.grid_current = grid_current
        self.grid_voltage = grid_voltage
        self.grid_frequency = grid_frequency
        self.output_power = output_power
        self.total_lifetime_kwh_high = total_lifetime_kwh_high
        self.total_lifetime_kwh_low = total_lifetime_kwh_low
