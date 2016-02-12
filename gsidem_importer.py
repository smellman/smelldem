import os
import concurrent.futures
from dem import DEM


def import_cmd(from_dir, to_dir, x, y, z):
    input_file = os.path.join(from_dir, "{z}/{x}/{y}.txt".format(x=x, y=y, z=z))
    output_file = os.path.join(to_dir, "{z}/{x}/{y}.smelldem".format(x=x, y=y, z=z))
    DEM.generateFromGSIDem(x, y, z, input_file, output_file)
    print(output_file)

class GSIDemImporter:
    def __init__(self, from_dir, to_dir, min_zoom, max_zoom):
        self.from_dir = from_dir
        self.to_dir = to_dir
        self.min_zoom = int(min_zoom)
        self.max_zoom = int(max_zoom)

    def run(self):
        self._prepare()
        self._convert()

    def _prepare(self):
        if not os.path.isdir(self.to_dir):
            os.mkdir(self.to_dir)
        for z in range(self.min_zoom, self.max_zoom + 1):
            output_dir = os.path.join(self.to_dir, str(z))
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)
            input_base = os.path.join(self.from_dir, str(z))
            print(input_base)
            _, xs, _ = next(os.walk(input_base))
            for x in xs:
                xdir = os.path.join(output_dir, x)
                if not os.path.isdir(xdir):
                    os.mkdir(xdir)

    def _convert(self):
        targets = []
        for z in range(self.min_zoom, self.max_zoom + 1):
            input_base = os.path.join(self.from_dir, str(z))
            _, xs, _ = next(os.walk(input_base))
            for x in xs:
                xdir = os.path.join(input_base, x)
                _, _, yfiles = next(os.walk(xdir))
                for yfile in yfiles:
                    sp = os.path.splitext(yfile)
                    if sp[1] == ".txt":
                        y = int(sp[0])
                        targets.append({"x":x, "y":y, "z":z})
        with concurrent.futures.ProcessPoolExecutor() as executor:
            {executor.submit(import_cmd, self.from_dir, self.to_dir, x = t["x"], y = t["y"], z = t["z"]): t for t in targets}

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description="Generate SmellDEM from GSI DEM")
    p.add_argument("input_dir", metavar="input_dir", help="Input dir")
    p.add_argument("output_dir", metavar="output_dir", help="Output dir")
    p.add_argument("min_zoom", metavar="min_zoom", help="Min zoom")
    p.add_argument("max_zoom", metavar="max_zoom", help="Max zoom")
    args = p.parse_args()
    print(args.input_dir, args.output_dir)
    g = GSIDemImporter(args.input_dir, args.output_dir, args.min_zoom, args.max_zoom)
    g.run()
