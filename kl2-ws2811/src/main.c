/**
 * Main file for the KL2-dev board
 */


#include "arm_cm0p.h"

#include <stddef.h>

#include "osc.h"
#include "leds.h"
#include "spi.h"

static uint8_t leds_buffer[150];

int main(void)
{
    SIM_SCGC5 |= SIM_SCGC5_PORTD_MASK;
    PORTD_PCR7 = PORT_PCR_MUX(1) | PORT_PCR_DSE_MASK;
    GPIOD_PDDR = 1 << 7;
    GPIOD_PDOR = 1 << 7;

    // Enable the bus clock output on PTC3 for debug purposes
    /*SIM_SCGC5 |= SIM_SCGC5_PORTC_MASK;
    SIM_SOPT2 |= SIM_SOPT2_CLKOUTSEL(2);
    PORTC_PCR3 = PORT_PCR_MUX(5);*/

    // Use the internal FLL. The circuit on my board for the external crystal
    // is badly designed and I believe its unstable.
    osc_set_fll(OSC_FLL_48MHZ, 0, 1);

    // Select the PLL for the USB clock source

    SIM_SCGC6 |= SIM_SCGC6_PIT_MASK;
    PIT_MCR = 0;
    PIT_LDVAL0 = 12000000; //250ms period on a 48MHz clock
    PIT_TCTRL0 = PIT_TCTRL_TIE_MASK | PIT_TCTRL_TEN_MASK;
    NVIC_ENABLE_IRQ(IRQ(INT_PIT));

    EnableInterrupts();

    spi_init();
    leds_init();

    uint8_t count = 0;
    while(1) {
        size_t t;
        spi_slave_read(leds_buffer, sizeof(leds_buffer), &t);
        leds_write(leds_buffer, sizeof(leds_buffer));
        count++;
    }
    return 0;
}

void PIT_IRQHandler()
{
    //GPIOD_PDOR = 0;
    GPIOD_PTOR = 1 << 7;
    PIT_TFLG0 = PIT_TFLG0;
}

