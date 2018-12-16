# Makefile for the KL26-based WS2811 USB dongle
#
# Kevin Cuzner
#

PROJECT = kl2-ws2811

# Project target
CPU = cortex-m0plus

# Source
SRCDIRS = src
GENSRCDIRS = src
BINDIR = bin
OBJDIR = obj
GENDIR = obj/gen
INCDIRS = include
LDINCDIRS =
CSRCDIRS = $(SRCDIRS)
SSRCDIRS = $(SRCDIRS)
SRC = $(foreach DIR,$(CSRCDIRS),$(wildcard $(DIR)/*.c))
GENSRC = $(foreach DIR,$(GENSRCDIRS),$(wildcard $(DIR)/*.c))
STORAGESRC = $(foreach DIR,$(CSRCDIRS),$(wildcard $(DIR)/*.storage.xml))
ASM = $(foreach DIR,$(SSRCDIRS),$(wildcard $(DIR)/*.s))


# Include directories
INCLUDE  = $(foreach DIR,$(INCDIRS),-I$(DIR)) -I$(GENDIR) -I.
LDINCLUDE = $(foreach DIR,$(LDINCDIRS),-L$(DIR))

# Linker
LSCRIPT = kl2-dev.ld

# C Flags
GCFLAGS  = -std=gnu99 -Wall -fno-common -mthumb -mcpu=$(CPU) -DSTM32F103xB --specs=nosys.specs -g -Wa,-ahlms=$(addprefix $(OBJDIR)/,$(notdir $(<:.c=.lst))) -O3
GCFLAGS += $(INCLUDE) -DUSB_DEBUG
CFLAGS  += $(GCFLAGS)
LDFLAGS += -T$(LSCRIPT) -mthumb -mcpu=$(CPU) -Wl,-Map,$(BINDIR)/$(PROJECT).map -nostartfiles
LDFLAGS += $(LDINCLUDE)
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

# Code Generation
PYTHON = python3
SCRIPTDIR = ./scripts
DESCRIPTORGEN = $(PYTHON) $(SCRIPTDIR)/descriptorgen.py

GENERATE =


#
# Build Targets
#

all:: $(BINDIR)/$(PROJECT).bin $(BINDIR)/$(PROJECT).hex

install: $(BINDIR)/$(PROJECT).bin $(BINDIR)/openocd.pid
	cat openocd/flash.cfg | nc localhost 4444

macros:
	$(CC) $(GCFLAGS) -dM -E - < /dev/null

cleanBuild: clean

clean: stop
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

## Build process

GENERATE_USB_DESCRIPTOR=USB_DESCRIPTOR
GENERATE_USB_DESCRIPTOR_SRC=_gen_usb_desc.c
GENERATE_USB_DESCRIPTOR_HDR=_gen_usb_desc.h

OBJ := $(addprefix $(OBJDIR)/,$(notdir $(SRC:.c=.o)))
OBJ += $(addprefix $(OBJDIR)/,$(notdir $(ASM:.s=.o)))
ifneq ($(filter $(GENERATE), $(GENERATE_USB_DESCRIPTOR)),)
	GEN_OBJ += $(GENDIR)/$(GENERATE_USB_DESCRIPTOR_SRC:.c=.o)
	GEN_TARGETS += $(GENERATE_USB_DESCRIPTOR)
endif
ALL_OBJ := $(OBJ) $(GEN_OBJ)
DEP := $(addprefix $(OBJDIR)/,$(notdir $(SRC:.c=.d)))

#
# Code generation
#
$(GENERATE_USB_DESCRIPTOR):
	@mkdir -p $(GENDIR)
	$(DESCRIPTORGEN) -os $(GENDIR)/$(GENERATE_USB_DESCRIPTOR_SRC) \
		-oh $(GENDIR)/$(GENERATE_USB_DESCRIPTOR_HDR) \
		$(GENSRC)


$(BINDIR)/$(PROJECT).hex: $(BINDIR)/$(PROJECT).elf
	$(OBJCOPY) -R .stack -O ihex $(BINDIR)/$(PROJECT).elf $(BINDIR)/$(PROJECT).hex

$(BINDIR)/$(PROJECT).bin: $(BINDIR)/$(PROJECT).elf
	$(OBJCOPY) -R .stack -O binary $(BINDIR)/$(PROJECT).elf $(BINDIR)/$(PROJECT).bin

$(BINDIR)/$(PROJECT).elf: $(ALL_OBJ)
	@mkdir -p $(dir $@)
	$(CC) $(ALL_OBJ) $(LDFLAGS) -o $(BINDIR)/$(PROJECT).elf
	$(OBJDUMP) -D $(BINDIR)/$(PROJECT).elf > $(BINDIR)/$(PROJECT).lst
	$(SIZE) $(BINDIR)/$(PROJECT).elf


# Generates compilation rules for the directory in $1
#
# Note to self: The double-dollar sign escapes the $ so that it doesn't get
# evaluated when this function is generated, but instead gets evaluated when
# Make is actually making.
define build_gcc_rules
$$(OBJDIR)/%.o: $1/%.c Makefile
	@mkdir -p $$(dir $$@)
	$$(CC) $$(GCFLAGS) -MMD -c $$< -o $$@
endef
define build_asm_rules
$$(OBJDIR)/%.o: $1/%.s Makefile
	@mkdir -p $$(dir $$@)
	$$(AS) $$(ASFLAGS) -o $$@ $$<
endef

# Generate rules for each source directory
$(foreach DIR,$(CSRCDIRS),$(eval $(call build_gcc_rules,$(DIR))))
$(foreach DIR,$(SSRCDIRS),$(eval $(call build_asm_rules,$(DIR))))

-include $(DEP)

# Ensure generated objects get run first
$(OBJ): | $(GEN_TARGETS)

