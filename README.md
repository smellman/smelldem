# SmellDEM

Binary format test for GSI's DEM Tile data.

Many features inspire by [Cesium quantized-mesh](http://cesiumjs.org/data-and-assets/terrain/formats/quantized-mesh-1.0.html).

# Structure

## header

```
struct Header
{
    unsigned int x;
    unsigned int y;
    unsigned char z;
    float maxHeight;
    float minHeight;
};
```

## Data availables

```
struct Availables
{
    unsigned char availables[256*256 / 8];
};
```

One value contain 8bit flag.

## Data

```
struct Data
{
    unsigned int length;
    unsigned short heights[length];
};
```

The heights array is zig-zag encoded.

# utility

## gsidem_reader.py

read tile data from GSI DEM file and write SmellDEM.

```bash
python gsidem_reader.py 5 28 13 ../qdltc/dem/5/28/13.txt 5.28.13.dem
```

## gsidem_writer.py

read tile data from SmellDEM and write GSI DEM file.

```bash
python gsidem_writer.py 5.28.12.dem 5.28.12.test.txt
```

## gsidem_importer.py

generate tile set from GSI DEM tile set.

```bash
python gsidem_importer.py ../qdltc/dem output2 0 12
```
