from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("K4"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("AA11"), IOStandard("LVCMOS33")),
    # Leds
    ("user_led", 0, Pins("D22"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("C22"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B22"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("B21"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("A21"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("C20"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("B20"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("A20"), IOStandard("LVCMOS33")),
    ("user_led_com", 0, Pins("H18"), IOStandard("LVCMOS33")),
    ("user_led_com", 1, Pins("G20"), IOStandard("LVCMOS33")),
    ("user_led_com", 2, Pins("F21"), IOStandard("LVCMOS33")),
    ("user_led_com", 3, Pins("E22"), IOStandard("LVCMOS33")),
    # UART
    (
        "serial",
        0,
        Subsignal("tx", Pins("D17")),
        Subsignal("rx", Pins("E17")),
        IOStandard("LVCMOS33"),
    ),
    # DDR3 SDRAM
    (
        "ddram",
        0,
        Subsignal(
            "a",
            Pins("V7 AA3 U5 T6 AB7 R6 AB2 W6", "AB1 Y4 AB5 AB3 AB6 AA4 AA1 Y6"),
            IOStandard("SSTL135"),
        ),
        Subsignal("ba", Pins("U6 AA6 V5"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("W4"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("W5"), IOStandard("SSTL135")),
        Subsignal("we_n", Pins("V4"), IOStandard("SSTL135")),
        Subsignal("cs_n", Pins("T5"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("Y2"), IOStandard("SSTL135")),
        Subsignal(
            "dq",
            Pins("U2 W2 U1 Y1 V3 W1 T1 V2"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal(
            "dqs_p",
            Pins("R3"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal(
            "dqs_n",
            Pins("R2"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal("clk_p", Pins("V9"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("V8"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke", Pins("AA5"), IOStandard("SSTL135")),
        Subsignal("odt", Pins("T4"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("R4"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),
    (
        "spisdcard",
        0,
        Subsignal("clk", Pins("F18")),
        Subsignal("mosi", Pins("F19"), Misc("PULLUP True")),
        Subsignal("cs_n", Pins("G18"), Misc("PULLUP True")),
        Subsignal("miso", Pins("E19"), Misc("PULLUP True")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
]

_connectors = []


class Platform(Xilinx7SeriesPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self, toolchain="vivado", device="xc7a200tfbg484-2"):
        Xilinx7SeriesPlatform.__init__(
            self, device, _io, _connectors, toolchain=toolchain
        )

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(
            self.lookup_request("clk100", loose=True), 1e9 / 100e6
        )
        # DDR3 SDRAM
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 34]")
