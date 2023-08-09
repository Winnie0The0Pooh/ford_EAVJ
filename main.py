#!/sbin/python3
import serial.tools.list_ports as port_list
import serial
import signal
from time import sleep
from threading import Thread
import argparse
import sys
import os
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from datetime import datetime

stop = False


def handler(signum, frame):
    print("Exiting...")

    global stop
    stop = True


def worker():
    while not stop:
        print("Read loop start")
        ff.write(s.read(size=1048576))
        print("Read loop end")

    s.close()
    ff.flush()
    ff.close()


def main():
    th = Thread(target=worker)
    th.start()
    while not stop:
        th.join(1)


def calc(filename):
    sp = filename.split(".")
    filename1 = sp[0] + "_proc1." + sp[1]
    # filename1 = "i:\\15\\out.txt"
    with open(filename, "rb") as f:
        with open(filename1, "w") as fw:

            resultsAccel = []
            resultsGyro = []

            recCount = 0
            goodRecCount = 0
            while True:
                res = f.read(16)

                if not res or len(res) < 16:  # if we get an empty string we've reached EOF
                    print(f"Reached end of file at {f.tell()}, file len was {os.path.getsize(filename)}", file=sys.stderr)
                    print(f"Total records: {recCount}, goodRecords: {goodRecCount}", file=sys.stderr)
                    break

                recCount += 1
                if res[14:16] != b'\r\n':
                    print(
                        f"Error in record, current pos: {f.tell()}, current record: {recCount}. Last 2 bytes are not \\r\\n!",
                        file=sys.stderr)
                    print(f"Bad record was: {res}", file=sys.stderr)
                    while True:
                        temp = f.read(2)
                        if temp == b'\r\n' or (temp[1] == b'\r' and f.read(1) == b'\n'):
                            print(f"New starting position: {f.tell()}", file=sys.stderr)
                            res = f.read(14)
                            break
                else:
                    goodRecCount += 1

                aX = int.from_bytes(res[0:2], byteorder="big", signed=True)
                aY = int.from_bytes(res[2:4], byteorder="big", signed=True)
                aZ = int.from_bytes(res[4:6], byteorder="big", signed=True)

                gX = int.from_bytes(res[8:10], byteorder="big", signed=True)
                gY = int.from_bytes(res[10:12], byteorder="big", signed=True)
                gZ = int.from_bytes(res[12:14], byteorder="big", signed=True)

                fA = sqrt(aX ** 2 + aY ** 2 + aZ ** 2)
                fG = sqrt(gX ** 2 + gY ** 2 + gZ ** 2)

                resultsAccel.append(aY)
                resultsGyro.append(fG)

                print(f"aX: {aX}, aY: {aY}, aZ: {aZ}, gX: {gX}, gY: {gY}, gZ: {gZ}")
                fw.write(f"{aX} {aY} {aZ} {gX} {gY} {gZ}\n")

            # fftAccel = np.array(resultsAccel)
            # sp = np.fft.fft(np.sin(fftAccel))
            # freq = np.fft.fftfreq(fftAccel.shape[-1])
            # plt.plot(freq, sp.real, freq, sp.imag)
            #
            # plt.show()

            # fftGyro = np.fft.fft(resultsGyro)

            # print(fftAccel)


if __name__ == "__main__":

    defaultFilename = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.txt'

    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("-p", "--port", type=str, help="COM port to use", default="COM3")
    ap.add_argument("-b", "--baudrate", type=int, help="Baud rate to use", default=230400)
    ap.add_argument("-s", "--bytesize", type=int, help="Byte size", default=serial.EIGHTBITS)
    ap.add_argument("-a", "--parity", type=str, help=f"Parity ({serial.PARITY_NAMES})", default=serial.PARITY_NONE,
                    choices=(
                    serial.PARITY_EVEN, serial.PARITY_MARK, serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_SPACE))
    ap.add_argument("-n", "--stopbits", type=int, help="Stopbits", default=serial.STOPBITS_ONE)
    ap.add_argument("-t", "--timeout", type=float, help="Timeout for reading in seconds", default=10.0)
    ap.add_argument("-l", "--list", action="store_true", help="List com ports and exit")
    ap.add_argument("-f", "--filename", type=str, help="File to write to or read from", default=defaultFilename)
    ap.add_argument("-c", "--calc", action="store_true", help="Calculate values from filename")
    args = ap.parse_args()

    if args.list:
        for p in port_list.comports():
            print(p)
        exit(0)

    if args.calc:
        calc(filename=args.filename)
        exit(0)

    s = serial.Serial(port=args.port, baudrate=args.baudrate, bytesize=args.bytesize,
                      parity=args.parity, stopbits=args.stopbits, timeout=args.timeout)
    ff = open(args.filename, "wb")

    signal.signal(signal.SIGINT, handler)

    doRead = True
    print(f"Launching reader for {args.port}")
    main()
