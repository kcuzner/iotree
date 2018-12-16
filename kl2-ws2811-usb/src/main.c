/**
 * Main file for the KL2-dev board
 */


#include "arm_cm0p.h"

#include <stddef.h>

#include "osc.h"
#include "usb.h"
#include "usb_app.h"
#include "leds.h"
#include "spi.h"

const USBApplicationSetup setup = {
    .interface_list = NULL,
};

const USBApplicationSetup *usb_app_setup = &setup;

/**
 * <descriptor id="device" type="0x01">
 *  <length name="bLength" size="1" />
 *  <type name="bDescriptorType" size="1" />
 *  <word name="bcdUSB">0x0200</word>
 *  <byte name="bDeviceClass">0</byte>
 *  <byte name="bDeviceSubClass">0</byte>
 *  <byte name="bDeviceProtocol">0</byte>
 *  <byte name="bMaxPacketSize0">USB_CONTROL_ENDPOINT_SIZE</byte>
 *  <word name="idVendor">0x16c0</word>
 *  <word name="idProduct">0x05dc</word>
 *  <word name="bcdDevice">0x0010</word>
 *  <ref name="iManufacturer" type="0x03" refid="manufacturer" size="1" />
 *  <ref name="iProduct" type="0x03" refid="product" size="1" />
 *  <byte name="iSerialNumber">0</byte>
 *  <count name="bNumConfigurations" type="0x02" size="1" />
 * </descriptor>
 * <descriptor id="lang" type="0x03" first="first">
 *  <length name="bLength" size="1" />
 *  <type name="bDescriptorType" size="1" />
 *  <foreach type="0x03">
 *    <echo name="wLang" />
 *  </foreach>
 * </descriptor>
 * <descriptor id="manufacturer" type="0x03" wIndex="0x0409">
 *  <property name="wLang" size="2">0x0409</property>
 *  <length name="bLength" size="1" />
 *  <type name="bDescriptorType" size="1" />
 *  <string name="wString">kevincuzner.com</string>
 * </descriptor>
 * <descriptor id="product" type="0x03" wIndex="0x0409">
 *  <property name="wLang" size="2">0x0409</property>
 *  <length name="bLength" size="1" />
 *  <type name="bDescriptorType" size="1" />
 *  <string name="wString">WS2811x USB Dongle</string>
 * </descriptor>
 * <descriptor id="configuration" type="0x02">
 *  <length name="bLength" size="1" />
 *  <type name="bDescriptorType" size="1" />
 *  <length name="wTotalLength" size="2" all="all" />
 *  <count name="bNumInterfaces" type="0x04" associated="associated" size="1" />
 *  <byte name="bConfigurationValue">1</byte>
 *  <byte name="iConfiguration">0</byte>
 *  <byte name="bmAttributes">0x80</byte>
 *  <byte name="bMaxPower">250</byte>
 *  <children type="0x04" />
 * </descriptor>
 */

static uint8_t leds_buffer[150];

static uint8_t leds_target[150];

uint32_t lfsr = 0x19abf3e1;

uint8_t lfsr_next(void) {
    unsigned lsb = lfsr & 0x1;
    lfsr >>= 1;
    if (lsb) {
        lfsr ^= 0x84000002;
    }

    return lfsr & 0xFF;
}

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

    // Set the PLL to 96MHz (divided by 2 for the 48MHz system clock and
    // by 2 again for the 24MHz bus clock).
    osc_set_pll(96000000, 1, 1);

    // Select the PLL for the USB clock source

    SIM_SCGC6 |= SIM_SCGC6_PIT_MASK;
    PIT_MCR = 0;
    PIT_LDVAL0 = 12000000; //250ms period on a 48MHz clock
    PIT_TCTRL0 = PIT_TCTRL_TIE_MASK | PIT_TCTRL_TEN_MASK;
    NVIC_ENABLE_IRQ(IRQ(INT_PIT));

    usb_init();

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

