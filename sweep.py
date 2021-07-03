#!/usr/bin/env python3

import sys
import os
import time

from rd6006 import RD6006
from ut61e import UT61E


def get_v_out(rd):
    return rd._read_register(10)/100


def get_i_out(rd):
    return rd._read_register(11)/1000


def check_device_file(fn):
    try:
        os.stat(fn)
    except Exception as e:
        print("Problem with serial port %s: %s" % (fn, str(e)), file=sys.stderr)
        sys.exit(2)


def read_dmm_voltage(dmm):
    dmm_v1 = dmm.get_meas()['val']
    dmm_v2 = dmm.get_meas()['val']
    dmm_v3 = dmm.get_meas()['val']
    return min(dmm_v1, dmm_v2, dmm_v3)


def main():
    if len(sys.argv) < 4:
        print("Usage %s [PSU_SERIAL_PORT] [DMM_SERIAL_PORT] [OUTPUT_FILE]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    max_voltage = 62  # adjust as needed!

    psu_serial_port = sys.argv[1]
    dmm_serial_port = sys.argv[2]
    output_filename = sys.argv[3]

    check_device_file(psu_serial_port)
    check_device_file(dmm_serial_port)

    rd = RD6006(psu_serial_port)
    dmm = UT61E(dmm_serial_port)

    # set initial current limit and zero voltage, then wait for PSU to settle
    rd.current = 0.1
    rd.voltage = 0
    time.sleep(2)

    with open(output_filename, "w") as fh:
        print('#v_set\tv_disp,\tv_dmm', file=fh)
        for v in range(0, max_voltage+1):
            rd.voltage = v
            time.sleep(0.3)  # wait for PSU to settle
            dmm_v = read_dmm_voltage(dmm)  # read DMM voltage
            disp_v = get_v_out(rd)  # read PSU display voltage
            err = disp_v - dmm_v

            # simpler than piping through tee(1) and then having
            # to deal with buffering etc
            print("%f\t%f\t%f\t%f" % (v, disp_v, dmm_v, err))
            print("%f\t%f\t%f\t%f" % (v, disp_v, dmm_v, err), file=fh)

    # save the PSU before exiting
    rd.current = 0
    rd.voltage = 0


if __name__ == "__main__":
    main()
