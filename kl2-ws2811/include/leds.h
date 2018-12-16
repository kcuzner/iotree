/**
 * WS2811 LED Driver
 *
 * Kevin Cuzner
 */

#ifndef _LEDS_H_
#define _LEDS_H_

#include <stdint.h>
#include <stddef.h>

void leds_init(void);

void leds_write(uint8_t *buffer, size_t length);

#endif //_LEDS_H_

