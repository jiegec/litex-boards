#!/usr/bin/env python3

from migen import *

from litex.gen import *

from litex_boards.platforms import digital_design

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT18KSF1G72HZ
from litedram.phy import s7ddrphy


# CRG ----------------------------------------------------------------------------------------------


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.cd_sys = ClockDomain()

        # dram
        self.cd_sys4x = ClockDomain()
        self.cd_sys4x_dqs = ClockDomain()
        self.cd_idelay = ClockDomain()

        # Clk/Rst
        clk100 = platform.request("clk100")
        rst = platform.request("cpu_reset")

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

        # DRAM
        pll.create_clkout(self.cd_sys4x, 4 * sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4 * sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay, 200e6)

        # IdelayCtrl.
        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)


# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=100e6, **kwargs):
        platform = digital_design.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            ident="LiteX SoC on Digital Design Board",
            **kwargs
        )

        # DDR3 SDRAM -------------------------------------------------------------------------------
        self.ddrphy = s7ddrphy.A7DDRPHY(
            platform.request("ddram"),
            memtype="DDR3",
            nphases=4,
            sys_clk_freq=sys_clk_freq,
        )
        self.add_sdram(
            "sdram",
            phy=self.ddrphy,
            # we have MT41K512M8, but they are the same thing
            module=MT18KSF1G72HZ(sys_clk_freq, "1:4"),
            l2_cache_size=kwargs.get("l2_size", 8192),
        )

        # Leds -------------------------------------------------------------------------------------
        self.leds = LedChaser(
            pads=platform.request_all("user_led"),
            sys_clk_freq=sys_clk_freq,
        )
        leds_com = platform.request_all("user_led_com")
        self.comb += leds_com.eq(0xF)

        # sdcard
        self.add_spi_sdcard()


# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(
        platform=digital_design.Platform,
        description="LiteX SoC on Digital Design Board.",
    )
    parser.add_target_argument(
        "--sys-clk-freq", default=100e6, type=float, help="System clock frequency."
    )
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=args.sys_clk_freq, **parser.soc_argdict)

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
