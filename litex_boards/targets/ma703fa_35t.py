#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from litex.gen import *

from litex_boards.platforms import ma703fa_35t

from litex.soc.cores.clock import *
from litex.soc.interconnect.axi import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.s7rgmii import LiteEthPHYRGMII


# CRG ----------------------------------------------------------------------------------------------
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset_n") | self.rst)
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_sys)


# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(
        self, sys_clk_freq=50e6, with_led_chaser=True, with_ethernet=True, **kwargs
    ):
        platform = ma703fa_35t.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(
            self, platform, sys_clk_freq, ident="LiteX SoC on MA703FA 35T", **kwargs
        )

        # Ethernet -------------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads=self.platform.request("eth_clocks", 0),
                pads=self.platform.request("eth", 0),
                iodelay_clk_freq=200e6,
                rx_delay=1e-9 # add additional delay for rx to work
            )
            self.add_ethernet(phy=self.ethphy)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads=platform.request_all("user_led"), sys_clk_freq=sys_clk_freq
            )


# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(
        platform=ma703fa_35t.Platform, description="LiteX SoC on MA703FA 35T."
    )
    parser.add_target_argument(
        "--sys-clk-freq", default=50e6, type=float, help="System clock frequency."
    )
    parser.add_argument(
        "--with-ethernet", action="store_true", help="Enable Ethernet support."
    )
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=args.sys_clk_freq,
        with_ethernet=args.with_ethernet,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
