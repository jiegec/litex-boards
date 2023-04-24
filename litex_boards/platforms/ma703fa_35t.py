#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform

_io = [
    # Clk / Rst
    ("clk50", 0, Pins("V4"), IOStandard("LVCMOS15")),
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
    # DDR3 SDRAM
    (
        "ddram",
        0,
        Subsignal(
            "a",
            Pins("AB3 AA6 Y3 Y2 AB6 AA3 Y7 AA4 AA8 Y4 Y9 AB7 AA5 W5"),
            IOStandard("SSTL15"),
        ),
        Subsignal("ba", Pins("AB2 AB5 W2"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("V2"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("AA1"), IOStandard("SSTL15")),
        Subsignal("we_n", Pins("W1"), IOStandard("SSTL15")),
        Subsignal("cs_n", Pins("Y1"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("P2 J6"), IOStandard("SSTL15")),
        Subsignal(
            "dq",
            Pins("P6 R1 M5 N4 N5 N2 M6 P1", "L3 J4 M3 K4 M2 K3 L4 L5"),
            IOStandard("SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal(
            "dqs_p",
            Pins("P5 M1"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal(
            "dqs_n",
            Pins("P4 L1"),
            IOStandard("DIFF_SSTL15"),
            Misc("IN_TERM=UNTUNED_SPLIT_40"),
        ),
        Subsignal("clk_p", Pins("T5"), IOStandard("DIFF_SSTL15")),
        Subsignal("clk_n", Pins("U5"), IOStandard("DIFF_SSTL15")),
        Subsignal("cke", Pins("Y6"), IOStandard("SSTL15")),
        Subsignal("odt", Pins("AB1"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("W4"), IOStandard("SSTL15")),
        Misc("SLEW=FAST"),
    ),
    # HDMI out
    (
        "hdmi_out",
        0,
        Subsignal(
            "clk_p", Pins("C18"), IOStandard("TMDS_33")
        ),
        Subsignal(
            "clk_n", Pins("C19"), IOStandard("TMDS_33")
        ),
        Subsignal(
            "data0_p",
            Pins("B15"),
            IOStandard("TMDS_33"),
        ),
        Subsignal(
            "data0_n",
            Pins("B16"),
            IOStandard("TMDS_33"),
        ),
        Subsignal(
            "data1_p",
            Pins("B21"),
            IOStandard("TMDS_33"),
        ),
        Subsignal(
            "data1_n",
            Pins("A21"),
            IOStandard("TMDS_33"),
        ),
        Subsignal(
            "data2_p",
            Pins("C22"),
            IOStandard("TMDS_33"),
        ),
        Subsignal(
            "data2_n",
            Pins("B22"),
            IOStandard("TMDS_33"),
        ),
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
