from dem import DEM

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description="Generate GSI DEM from SmellDEM")
    p.add_argument("input_file", metavar="input_file", help="Input file")
    p.add_argument("output_file", metavar="output_file", help="Output file")
    args = p.parse_args()
    print(args.input_file, args.output_file)
    DEM.readDEMandWriteGSIDEM(args.input_file, args.output_file)
