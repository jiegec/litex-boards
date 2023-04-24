#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("V4"), IOStandard("LVCMOS33")),
    ("cpu_reset_n", 0, Pins("R14"), IOStandard("LVCMOS33")),
    # Leds
    ("user_led", 0, Pins("E21"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("D21"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("E22"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("D22"), IOStandard("LVCMOS33")),
    # UART
    (
        "serial",
        0,
        Subsignal("tx", Pins("R17")),
        Subsignal("rx", Pins("P16")),
        IOStandard("LVCMOS33"),
    ),
    # RGMII Ethernet
    (
        "eth_clocks",
        0,
        Subsignal("tx", Pins("AB21")),
        Subsignal("rx", Pins("W19")),
        IOStandard("LVCMOS33"),
    ),
    (
        "eth",
        0,
        Subsignal("rx_ctl", Pins("V18")),
        Subsignal("rx_data", Pins("V19 W20 AA20 AA21")),
        Subsignal("tx_ctl", Pins("AB22")),
        Subsignal("tx_data", Pins("W21 W22 Y21 Y22")),
        Subsignal("rst_n", Pins("U17")),
        Subsignal("mdio", Pins("N17")),
        Subsignal("mdc", Pins("U18")),
        IOStandard("LVCMOS33"),
    ),
]

_connectors = []


class Platform(Xilinx7SeriesPlatform):
    default_clk_name = "clk50"
    default_clk_period = 20.0

    def __init__(self, toolchain="vivado", device="xc7a35tfgg484-2"):
        Xilinx7SeriesPlatform.__init__(
            self, device, _io, _connectors, toolchain=toolchain
        )

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9 / 50e6)
