/**
 * Oscillator abstraction
 *
 * ws2811-usb
 *
 * Kevin Cuzner
 */

#include "osc.h"

void osc_set_fll(OscFllFrequency frequency, uint8_t sysclkdiv, uint8_t busclkdiv)
{
    //1: Enable the internal oscillator (4MHz) and set the MCG to FBI
    //mode

    MCG_C1 |= MCG_C1_IRCLKEN_MASK;
    MCG_C1 = (MCG_C1 & ~MCG_C1_CLKS_MASK) | MCG_C1_CLKS(1);
    while ((MCG_S & MCG_S_CLKST_MASK) != MCG_S_CLKST(1)) { }
    MCG_C2 |= MCG_C2_IRCS_MASK;
    while ((MCG_S & MCG_S_IRCST_MASK) != MCG_S_IRCST_MASK) { }

    //2: Set the FLL frequency and update the clock dividers (at 4MHz,
    //all frequencies are safe)
    
    MCG_C1 |= MCG_C1_IREFS_MASK;
    while ((MCG_S & MCG_S_IREFST_MASK) != MCG_S_IREFST_MASK) { }
    MCG_C4 = (MCG_C4 & MCG_C4_FCTRIM_MASK & MCG_C4_SCFTRIM_MASK) |
        MCG_C4_DMX32_MASK | MCG_C4_DRST_DRS(1);
    while ((MCG_C4 & MCG_C4_DRST_DRS_MASK) != MCG_C4_DRST_DRS(1)) { }

    SIM_CLKDIV1 = SIM_CLKDIV1_OUTDIV1(sysclkdiv) | SIM_CLKDIV1_OUTDIV4(busclkdiv);

    //3: Once the FLL has locked, move to FEI mode
    
    MCG_C1 = (MCG_C1 & ~MCG_C1_CLKS_MASK) | MCG_C1_CLKS(0);
    while ((MCG_S & MCG_S_CLKST_MASK) != MCG_S_CLKST(1)) { }
}

