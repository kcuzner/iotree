# Makefile for the KL26-based WS2811 USB dongle
#
# Kevin Cuzner
#

PROJECT = kl2-ws2811

# Project Structure
SRCDIR = src
BINDIR = bin
OBJDIR = obj
INCDIR = include

# Project target
CPU = cortex-m0plus

# Source
SRC = $(wildcard $(SRCDIR)/*.c)
ASM = $(wildcard $(SRCDIR)/*.S)

# Include directories
INCLUDE  = -I$(INCDIR)

# Linker 
LSCRIPT = kl2-dev.ld

# C Flags
GCFLAGS  = -std=gnu99 -Wall -fno-common -mthumb -mcpu=$(CPU) -DSTM32F103xB --specs=nosys.specs -g -Wa,-ahlms=$(addprefix $(OBJDIR)/,$(notdir $(<:.c=.lst)))
GCFLAGS += $(INCLUDE)
LDFLAGS += -T$(LSCRIPT) -mthumb -mcpu=$(CPU) -Wl,-Map,$(BINDIR)/$(PROJECT).map -nostartfiles
ASFLAGS += -mcpu=$(CPU)

# Flashing
OCDFLAGS = -f openocd/openocd.cfg

# Tools
CC = arm-none-eabi-gcc
AS = arm-none-eabi-as
AR = arm-none-eabi-ar
LD = arm-none-eabi-ld
OBJCOPY = arm-none-eabi-objcopy
SIZE = arm-none-eabi-size --format=SysV
OBJDUMP = arm-none-eabi-objdump
OCD = openocd
GDB = arm-none-eabi-gdb

RM = rm -rf

## Build process

OBJ := $(addprefix $(OBJDIR)/,$(notdir $(SRC:.c=.o)))
OBJ += $(addprefix $(OBJDIR)/,$(notdir $(ASM:.S=.o)))

all:: $(BINDIR)/$(PROJECT).bin $(BINDIR)/$(PROJECT).hex

install: $(BINDIR)/$(PROJECT).bin $(BINDIR)/openocd.pid
	cat openocd/flash.cfg | nc localhost 4444

$(BINDIR)/$(PROJECT).hex: $(BINDIR)/$(PROJECT).elf
	$(OBJCOPY) -R .stack -O ihex $(BINDIR)/$(PROJECT).elf $(BINDIR)/$(PROJECT).hex

$(BINDIR)/$(PROJECT).bin: $(BINDIR)/$(PROJECT).elf
	$(OBJCOPY) -R .stack -O binary $(BINDIR)/$(PROJECT).elf $(BINDIR)/$(PROJECT).bin

$(BINDIR)/$(PROJECT).elf: $(OBJ)
	@mkdir -p $(dir $@)
	$(CC) $(OBJ) $(LDFLAGS) -o $(BINDIR)/$(PROJECT).elf
	$(OBJDUMP) -D $(BINDIR)/$(PROJECT).elf > $(BINDIR)/$(PROJECT).lst
	$(SIZE) $(BINDIR)/$(PROJECT).elf

macros:
	$(CC) $(GCFLAGS) -dM -E - < /dev/null

cleanBuild: clean

clean:
	$(RM) $(BINDIR)
	$(RM) $(OBJDIR)

size:
	$(SIZE) $(BINDIR)/$(PROJECT).elf

#
# Debug
#

start: $(BINDIR)/openocd.pid

stop:
	-echo shutdown | nc localhost 4444

$(BINDIR)/openocd.pid:
	openocd/run-openocd-server.sh $(OCD) $@

gdb:
	$(GDB) -ex "target remote alarmpi:3333" $(BINDIR)/$(PROJECT).elf

# Compilation
$(OBJDIR)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(GCFLAGS) -c $< -o $@

$(OBJDIR)/%.o: $(SRCDIR)/%.S
	@mkdir -p $(dir $@)
	$(AS) $(ASFLAGS) -o $@ $<

