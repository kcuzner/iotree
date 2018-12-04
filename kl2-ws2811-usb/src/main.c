/**
 * Main file for the KL2-dev board
 */

#include "arm_cm0p.h"

#include "osc.h"
#include "usb.h"

int main(void)
{
    SIM_SCGC5 |= SIM_SCGC5_PORTD_MASK;
    PORTD_PCR7 = PORT_PCR_MUX(1) | PORT_PCR_DSE_MASK;
    GPIOD_PDDR = 1 << 7;
    GPIOD_PDOR = 1 << 7;

    // Enable the bus clock output on PTC3 for debug purposes
    SIM_SCGC5 |= SIM_SCGC5_PORTC_MASK;
    SIM_SOPT2 |= SIM_SOPT2_CLKOUTSEL(2);
    PORTC_PCR3 = PORT_PCR_MUX(5);

    // Set the PLL to 96MHz (divided by 2 for the 48MHz system clock and
    // by 2 again for the 24MHz bus clock).
    osc_set_pll(96000000, 1, 1);
    
    // Select the PLL for the USB clock source

    SIM_SCGC6 |= SIM_SCGC6_PIT_MASK;
    PIT_MCR = 0;
    PIT_LDVAL0 = 12000000; //250ms period on a 48MHz clock
    PIT_TCTRL0 = PIT_TCTRL_TIE_MASK | PIT_TCTRL_TEN_MASK;
    NVIC_ISER = 1 << IRQ(INT_PIT);

    //usb_init();

    EnableInterrupts();

    while(1) {
    }
    return 0;
}

void PIT_IRQHandler()
{
    //GPIOD_PDOR = 0;
    GPIOD_PTOR = 1 << 7;
    PIT_TFLG0 = PIT_TFLG0;
}

