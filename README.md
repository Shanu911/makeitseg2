# makeitseg2

`makeitseg2` is a python module that converts SEGY or SU (Seismic Un*x) files to SEG2 (or DAT) files.
## Getting Started

A working example is provided in the "test.ipynb" file.
### Prerequisites

Before installing `makeitseg2`, ensure that `obspy` is installed. You can install it via pip using the following command:
```
pip install obspy
```
### Installation 
You can install `makeitseg2` via pip using the following command:

```
pip install makeitseg2
```
### How it works
To use `makeitseg2`, you can import it and call the `convert` function, passing in the name of the SEGY or SU file and an optional name for the new converted SEG2 file.
``` python
 import makeitseg2
 makeitseg2.convert(SEGY_or_SU_filename, newConverted_SEG2_file_name)
```

If `newConverted_SEG2_file_name` is not provided, the new SEG2 file will have the same name as the original and will be placed in the `Converted_SEG2` folder.
