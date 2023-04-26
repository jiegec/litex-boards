#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2023 Jiajie Chen <c@jia.je>
# SPDX-License-Identifier: BSD-2-Clause

from litex.gen import *

from litex_boards.platforms import ma703fa_35t

from litex.soc.cores.clock import *
from litex.soc.cores.video import VideoS7HDMIPHY
from litex.soc.interconnect.axi import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy


# CRG ----------------------------------------------------------------------------------------------
class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_idelay = ClockDomain()

        self.cd_sys4x = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()

        self.cd_hdmi = ClockDomain()
        self.cd_hdmi5x = ClockDomain()

        # # #

        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset_n") | self.rst)
        clk50 = platform.request("clk50")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_idelay, 200e6)

        pll.create_clkout(self.cd_sys4x, 4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        self.video_pll = video_pll = S7PLL(speedgrade=-1)
        video_pll.register_clkin(clk50, 50e6)
        pix_clk = 89.01e6
        video_pll.create_clkout(self.cd_hdmi, pix_clk)
        video_pll.create_clkout(self.cd_hdmi5x, 5 * pix_clk)


# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(
        self,
        sys_clk_freq=100e6,
        with_led_chaser=True,
        with_ethernet=True,
        with_video_terminal=True,
        **kwargs
    ):
        platform = ma703fa_35t.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(
            self, platform, sys_clk_freq, ident="LiteX SoC on MA703FA 35T", **kwargs
        )

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = s7ddrphy.A7DDRPHY(
                platform.request("ddram"),
                memtype="DDR3",
                nphases=4,
                sys_clk_freq=sys_clk_freq,
            )
            self.add_sdram(
                "sdram",
                phy=self.ddrphy,
                module=MT41K128M16(sys_clk_freq, "1:4"),
                l2_cache_size=kwargs.get("l2_size", 8192),
            )

        # Ethernet -------------------------------------------------------------------------------------
        if with_ethernet:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads=self.platform.request("eth_clocks", 0),
                pads=self.platform.request("eth", 0),
                iodelay_clk_freq=200e6,
            )
            self.add_ethernet(phy=self.ethphy)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.videophy = VideoS7HDMIPHY(
                platform.request("hdmi_out"), clock_domain="hdmi"
            )
            self.add_video_terminal(
                phy=self.videophy, timings="1920x1080@30Hz", clock_domain="hdmi"
            )

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
        "--sys-clk-freq", default=100e6, type=float, help="System clock frequency."
    )
    parser.add_argument(
        "--with-ethernet", action="store_true", help="Enable Ethernet support."
    )
    parser.add_target_argument(
        "--with-video-terminal",
        action="store_true",
        help="Enable Video Terminal (HDMI).",
    )
    parser.add_argument(
        "--with-spi-sdcard", action="store_true", help="Enable SPI-mode SDCard support."
    )
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq=args.sys_clk_freq,
        with_ethernet=args.with_ethernet,
        with_video_terminal=args.with_video_terminal,
        **parser.soc_argdict,
    )

    if args.with_spi_sdcard:
        soc.add_spi_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
