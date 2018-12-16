/**
 * WS2811 LED Driver
 *
 * Kevin Cuzner
 */

#include "leds.h"

#include "arm_cm0p.h"

#define LEDS_BIT_ZERO 12
#define LEDS_BIT_ONE  29

void leds_init(void)
{
    // The LEDs are attached to PTC1.
    // We will use AF5 to connect it to TPM0_CH0.
    SIM_SCGC5 |= SIM_SCGC5_PORTC_MASK;
    PORTC_PCR1 = PORT_PCR_MUX(4);
    SIM_SCGC6 |= SIM_SCGC6_TPM0_MASK | SIM_SCGC6_DMAMUX_MASK;

    // TPM clock source is 48MHz clock
    SIM_SOPT2 &= ~SIM_SOPT2_TPMSRC_MASK;
    SIM_SOPT2 |= SIM_SOPT2_TPMSRC(1);

    TPM0_SC = 0; //disable counter
    TPM0_MOD = 60; //800KHz clock at a 48MHz input
    TPM0_C0SC = TPM_CnSC_MSB_MASK | TPM_CnSC_ELSB_MASK;
    TPM0_C0V = 0;
}

uint32_t led_count = 0;

void leds_write(uint8_t *buffer, size_t length)
{
    // Perform a reset of zeros
    TPM0_C0V = 0;
    TPM0_SC = TPM_SC_CMOD(1); //start counter, 0 prescaler, module clock, upcounting PWM.

    // Reset is 50us, or at least 40 periods
    for (uint8_t i = 0; i < 50; i++)
    {
        while (!(TPM0_SC & TPM_SC_TOF_MASK)) { }
        TPM0_SC |= TPM_SC_TOF_MASK;
    }

    for (uint8_t i = 0; i < length; i++)
    {
        // Send data bitwise, LSB first
        for (uint8_t j = 0x80; j != 0; j >>= 1)
        {
            // Determine next bit
            TPM0_C0V = buffer[i] & j ? LEDS_BIT_ONE : LEDS_BIT_ZERO;
            // Wait for it to be registered
            while (!(TPM0_SC & TPM_SC_TOF_MASK)) { }
            TPM0_SC |= TPM_SC_TOF_MASK;
        }
    }

    led_count++;
}

