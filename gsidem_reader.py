from dem import DEM

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description="Generate SmellDEM from GSI DEM")
    p.add_argument("z", metavar="z", help="z")
    p.add_argument("x", metavar="x", help="x")
    p.add_argument("y", metavar="y", help="y")
    p.add_argument("input_file", metavar="input_file", help="Input file")
    p.add_argument("output_file", metavar="output_file", help="Output file")
    p.add_argument('--gzip', help='gzipped output', action="store_true")
    args = p.parse_args()
    print(args.x, args.y, args.z, args.input_file, args.output_file, args.gzip)
    DEM.generateFromGSIDem(args.x, args.y, args.z, args.input_file, args.output_file, args.gzip)
