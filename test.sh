#!/bin/sh

# ---- Global variables ----

input=/dev/input/event0
code_prefix="ABS"
code_prefix="KEY"
code="${code_prefix}_[XY]"
code="BTN_TOUCH"
val_regex=".*(\(BTN_TOUCH\)), value \([-]\?[0-9]\+\)"
val_subst="\2"

# ---- Functions ----
# http://stackoverflow.com/questions/28841139/how-to-get-coordinates-of-touchscreen-rawdata-using-linux

send_axis() {
    # 1. Convert axis value ($1) from device specific units
    # 2. Send this axis value via UDP packet
    echo $1
}

process_line() {  
    flag=$(cat /sys/class/backlight/rpi_backlight/bl_power)
    while read line; do
        axis=$(echo $line | grep "^Event:" | grep $code | \
               sed "s/$val_regex/$val_subst/")
	
        if [ -n "$axis" ]; then
            if [ "$axis" -eq 1 ]; then
              { [ "$flag" -eq "0" ] && flag="1" || flag="0"; }
              echo $flag > /sys/class/backlight/rpi_backlight/bl_power
            fi
        fi
    done
}

# ---- Entry point ----

if [ $(id -u) -ne 0 ]; then
    echo "This script must be run from root" >&2
    exit 1
fi

evtest $input | process_line
