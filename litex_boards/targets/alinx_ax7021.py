#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex_boards.platforms import alinx_ax7021

from litex.soc.cores.clock import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_vga):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_vga    = ClockDomain()

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)
        clk50 = platform.request("clk50")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # Video PLL
        if with_vga:
            pll.create_clkout(self.cd_vga, 40e6)
        
# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6,
        with_led_chaser=True,
        with_video_terminal=True,
        **kwargs):
        platform = alinx_ax7021.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, with_vga=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("uart_name", "serial") == "serial":
            # Defaults to JTAG-UART since UART is connected to PS instead of PL
            kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Alinx AX7021", **kwargs)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            vga = platform.request("vga")
            self.comb += [vga.reset_n.eq(~self.crg.rst)]
            self.videophy = VideoVGAPHY(vga, clock_domain="vga")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=alinx_ax7021.Platform, description="LiteX SoC on zynq xc7z020.")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        with_video_terminal = args.with_video_terminal,
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
