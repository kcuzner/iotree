/**
 * SPI Slave
 *
 * Kevin Cuzner
 */

#ifndef _SPI_H_
#define _SPI_H_

#include <stddef.h>
#include <stdint.h>

/**
 * This is a very simple one-way SPI "bucket". The master will send a
 * bunch of bytes. The value returned by the microcontroller will be an
 * "acknowledge" or "notacknowledge" value indicating if there was space
 * in the buffer to accept the data.
 */

void spi_init(void);

/**
 * Blocks until some bytes have been read by the SPI Slave
 *
 * buffer: Buffer to read into
 * length: Buffer length
 * read: Number of bytes read
 */
void spi_slave_read(void *buffer, size_t length, size_t *read);

#endif //_SPI_H_

