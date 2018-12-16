/**
 * SPI Slave
 *
 * Kevin Cuzner
 */

#include "spi.h"

#include "arm_cm0p.h"

void spi_init(void)
{
    // Start the SPI and Port C
    SIM_SCGC4 |= SIM_SCGC4_SPI0_MASK;
    SIM_SCGC5 |= SIM_SCGC5_PORTC_MASK;

    // Place the SPI in slave mode
    SPI0_C1 = SPI_C1_CPHA_MASK;

    // Select ALT2 for PTC4-PTC7
    PORTC_PCR4 = PORT_PCR_MUX(2);
    PORTC_PCR5 = PORT_PCR_MUX(2);
    PORTC_PCR6 = PORT_PCR_MUX(2);
    PORTC_PCR7 = PORT_PCR_MUX(2);
}

void spi_slave_read(void *buffer, size_t length, size_t *read)
{
    // Enable the SPI
    SPI0_C1 |= SPI_C1_SPE_MASK;

    for (*read = 0; *read < length; *read = *read + 1)
    {
        while (!(SPI0_S & SPI_S_SPRF_MASK)) { }

        ((uint8_t *)buffer)[*read] = SPI0_DL;
    }

    // Disable SPI
    SPI0_C1 &= ~SPI_C1_SPE_MASK;
    // Read the data register to flush (necessary?)
    SPI0_DL;
}

