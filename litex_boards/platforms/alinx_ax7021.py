#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Yonggang Liu <ggang.liu@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk50",    0, Pins("Y9"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("A16"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_btn", 0, Pins("A17"), IOStandard("LVCMOS33")),

    # Serial in J15
    ("serial", 0,
        Subsignal("tx", Pins("T21"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("U21"), IOStandard("LVCMOS33")),
    ),

    # VGA
    ("vga", 0,
        Subsignal("clk", Pins("G16")),
        Subsignal("reset_n", Pins("C17")),
        Subsignal("hsync", Pins("E19")),
        Subsignal("vsync", Pins("F16")),
        Subsignal("de", Pins("E20")),
        Subsignal("r", Pins("H22 G22 G17 F17 G15 D15 E15 F18")),
        Subsignal("g", Pins("E18 H17 H18 H19 H20 G19 F19 G20")),
        Subsignal("b", Pins("G21 F21 F22 E21 D21 D22 C22 B21")),
        IOStandard("LVCMOS33")
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = []

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self):
        Xilinx7SeriesPlatform.__init__(self, "xc7z020clg484-2", _io, _connectors, toolchain="vivado")

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
