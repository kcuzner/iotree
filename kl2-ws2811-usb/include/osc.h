/**
 * Oscillator abstraction
 *
 * ws2811-usb
 *
 * Kevin Cuzner
 */

#ifndef _OSC_H_
#define _OSC_H_

#include "arm_cm0p.h"
#include <stdint.h>

#define OSC_EXTERNAL_FREQ 12000000
#define OSC_PLL_PRDIV     2 //divide by 3 for 4MHz

/**
 * Clock definitions for my own reference
 *
 * Core Clock: Clocks the Cortex-M0+ core
 * Platform Clock: Clocks the crossbar switch and NVIC
 * System Clock: Clocks the bus masters
 * Bus/Flash Clock: Clocks the bus slaves and peripherals
 *
 * While the Core/Platform/System clock can go up to 48MHz, the
 * Bus/Flash clock has a maximum of 24MHz.
 */

typedef enum {
    OSC_FLL_24MHZ = 0x00,
    OSC_FLL_48MHZ = 0x01,
    OSC_FLL_72MHZ = 0x02,
    OSC_FLL_96MHZ = 0x03
} OscFllFrequency;

/**
 * Configures the FLL to use the internal source
 *
 * frequency: FLL DCO frequency selection
 * sysclkdiv: Clock divider for the main system clock, platform clock,
 * and core clock
 * busclkdiv: Clock divider in addition to the sysclkdiv for the bus
 * clock and flash clock.
 */
void osc_set_fll(OscFllFrequency frequency, uint8_t sysclkdiv, uint8_t busclkdiv);

/**
 * Configures the PLL to use an external crystal
 */
void osc_set_pll(uint32_t frequency, uint8_t sysclkdiv, uint8_t busclkdiv);


#endif //_OSC_H_

