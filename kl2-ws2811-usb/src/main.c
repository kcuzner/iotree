/**
 * Main file for the KL2-dev board
 */

#include "arm_cm0p.h"
#include "bootloader.h"

#include "usb.h"

int main(void)
{
    SIM_SCGC5 |= SIM_SCGC5_PORTD_MASK;
    PORTD_PCR7 = PORT_PCR_MUX(1) | PORT_PCR_DSE_MASK;
    GPIOD_PDDR = 1 << 7;
    GPIOD_PDOR = 1 << 7;

    SIM_SCGC6 |= SIM_SCGC6_PIT_MASK;
    PIT_MCR = 0;
    PIT_LDVAL0 = 12000000; //250ms period on a 48MHz clock
    PIT_TCTRL0 = PIT_TCTRL_TIE_MASK | PIT_TCTRL_TEN_MASK;
    NVIC_ISER = 1 << IRQ(INT_PIT);


    //move to FBI, prep for allowing FLL to reach its target frequency
    MCG_C2 = MCG_C2_LOCRE0_MASK | MCG_C2_FCFTRIM_MASK | MCG_C2_IRCS_MASK;
    MCG_C6 = 0;


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

