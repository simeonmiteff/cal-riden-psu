#!/usr/bin/env python3

import sys
import os

from rd6006 import RD6006


def display_cal(regs):
    print("OUTPUT V ZERO\t", regs[0])
    print("OUTPUT V SCALE\t", regs[1])
    print("BACK   V ZERO\t", regs[2])
    print("BACK   V SCALE\t", regs[3])
    print("OUTPUT I ZERO\t", regs[4])
    print("OUTPUT I SCALE\t", regs[5])
    print("BACK   I ZERO\t", regs[6])
    print("BACK   I SCALE\t", regs[7])


def get_integer(msg, i):
    # Read an integer from a prompt on stdin (with a default value)
    while True:
        try:
            v = input(msg + "\t [%d]: " % i)
        except KeyboardInterrupt:
            print("Exiting.")
            sys.exit(1)
        if v.strip() != "":
            try:
                i = int(v)
            except ValueError:
                print('"%s" is not an integer, try again' % v)
                continue
        return i


def set_panel_locked(rd, locked):
    # Toggle the front panel lock
    rd._write_register(15, int(locked))


def prompt_calibration_registers(regs):
    return [get_integer("OUTPUT V ZERO", regs[0]), get_integer("OUTPUT V SCALE", regs[1]),
            get_integer("BACK   V ZERO", regs[2]), get_integer("BACK   V SCALE", regs[3]),
            get_integer("OUTPUT I ZERO", regs[4]), get_integer("OUTPUT I SCALE", regs[5]),
            get_integer("BACK   I ZERO", regs[6]), get_integer("BACK   I SCALE", regs[7])]


def write_calibration_registers(rd, regs):
    set_panel_locked(rd, True)
    for address, value in zip(range(55, 63), regs):
        print("Writing %d = %d" % (address, value))
        rd._write_register(address, value)
    # magic register/value to commit cal registers to nvram
    # 01 06 00 36 15 01 a6 94
    # 0x54 = 36
    # 0x1501 = 5377
    rd._write_register(54, 5377)
    set_panel_locked(rd, False)
    print("Done.")


def main():
    if len(sys.argv) < 2:
        print("Usage %s [SERIAL_PORT]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    serial_port = sys.argv[1]
    try:
        os.stat(serial_port)
    except Exception as e:
        print("Problem with serial port %s: %s" % (serial_port, str(e)), file=sys.stderr)
        sys.exit(2)

    rd = RD6006(serial_port)

    cal_registers = rd._read_registers(55, 62)
    print("Current calibration registers:")
    display_cal(cal_registers)

    print("\nEnter new calibration registers:")
    new_registers = prompt_calibration_registers(cal_registers)

    print("\nWriting new calibration registers:")
    write_calibration_registers(rd, new_registers)

    print("\nReading back new calibration registers:")
    cal_registers = rd._read_registers(55, 62)[:8]
    display_cal(cal_registers)

    if new_registers != cal_registers:
        print("\nFailed to write new registers:\n\tWritten: %s\n\tRead:    %s" %
              (str(new_registers), str(cal_registers)))
        sys.exit(3)
    else:
        print("\nNew registers were written successfully.")


if __name__ == "__main__":
    main()
