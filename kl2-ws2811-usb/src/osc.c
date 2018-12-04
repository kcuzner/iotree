/**
 * Oscillator abstraction
 *
 * ws2811-usb
 *
 * Kevin Cuzner
 */

#include "osc.h"

/**
 * Moves the internal clock to the fast internal RC oscillator
 */
static void osc_set_irc(void)
{
    MCG_C1 |= MCG_C1_IRCLKEN_MASK;
    MCG_C1 = (MCG_C1 & ~MCG_C1_CLKS_MASK) | MCG_C1_CLKS(1);
    while ((MCG_S & MCG_S_CLKST_MASK) != MCG_S_CLKST(1)) { }
    MCG_C2 |= MCG_C2_IRCS_MASK;
    while ((MCG_S & MCG_S_IRCST_MASK) != MCG_S_IRCST_MASK) { }
}

void osc_set_fll(OscFllFrequency frequency, uint8_t sysclkdiv, uint8_t busclkdiv)
{
    //1: Enable the internal oscillator (4MHz) and set the MCG to FBI
    //mode

    osc_set_irc();

    //2: Set the FLL frequency and update the clock dividers (at 4MHz,
    //all frequencies are safe)

    MCG_C1 |= MCG_C1_IREFS_MASK;
    while ((MCG_S & MCG_S_IREFST_MASK) != MCG_S_IREFST_MASK) { }
    MCG_C4 = (MCG_C4 & MCG_C4_FCTRIM_MASK & MCG_C4_SCFTRIM_MASK) |
        MCG_C4_DMX32_MASK | MCG_C4_DRST_DRS(frequency);
    while ((MCG_C4 & MCG_C4_DRST_DRS_MASK) != MCG_C4_DRST_DRS(frequency)) { }

    SIM_CLKDIV1 = SIM_CLKDIV1_OUTDIV1(sysclkdiv) | SIM_CLKDIV1_OUTDIV4(busclkdiv);

    //3: Once the FLL has locked, move to FEI mode

    MCG_C1 = (MCG_C1 & ~MCG_C1_CLKS_MASK) | MCG_C1_CLKS(0);
    while ((MCG_S & MCG_S_CLKST_MASK) != MCG_S_CLKST(0)) { }

    // The PLLFLL clock is now the FLL
    SIM_SOPT2 &= ~SIM_SOPT2_PLLFLLSEL_MASK;
}

void osc_set_pll(uint32_t frequency, uint8_t sysclkdiv, uint8_t busclkdiv)
{
    uint32_t vdiv = MCG_C6_VDIV0(frequency /
            (OSC_EXTERNAL_FREQ / (OSC_PLL_PRDIV + 1)) - 24);

    // Set us for FBI

    osc_set_irc();

    // Activate the oscillator and wait for it to start up

    MCG_C2 = MCG_C2_LOCRE0_MASK | MCG_C2_FCFTRIM_MASK | MCG_C2_RANGE0(1) |
        MCG_C2_EREFS0_MASK | MCG_C2_IRCS_MASK;
    OSC0_CR = OSC_CR_ERCLKEN_MASK;
    while (!(MCG_S & MCG_S_OSCINIT0_MASK)) { }

    // Set up the PLL and turn it on

    MCG_C6 = vdiv;
    MCG_C5 = MCG_C5_PLLCLKEN0_MASK | MCG_C5_PRDIV0(OSC_PLL_PRDIV);
    while (!(MCG_S & MCG_S_LOCK0_MASK)) { }

    // Select the PLL as the output when mode 0 is selected

    MCG_C6 |= MCG_C6_PLLS_MASK;
    while (!(MCG_S & MCG_S_PLLST_MASK)) { }

    // Set the dividers
    SIM_CLKDIV1 = SIM_CLKDIV1_OUTDIV1(sysclkdiv) | SIM_CLKDIV1_OUTDIV4(busclkdiv);

    // Set the PLLFLL clock to be the PLL divided by 2
    SIM_SOPT2 |= SIM_SOPT2_PLLFLLSEL_MASK;

    // Move to PEE mode
    MCG_C1 = (MCG_C1 & ~MCG_C1_CLKS_MASK) | MCG_C1_CLKS(3);
    while ((MCG_S & MCG_S_CLKST_MASK) != MCG_S_CLKST(3)) { }
}

