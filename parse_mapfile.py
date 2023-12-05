#! /usr/bin/env python3

import argparse
import collections
import os
import sys

from mapfile_parser import mapfile

def printMapFile(m):
    for segment in m:
        print(f'segment {segment.name:<40} vram={segment.vram:08X} size={segment.size:08X} vrom={segment.vrom:08X}')
        for file in segment:
            print(f'  file {str(file.filepath):<40} vram={file.vram:08X} size={file.size:08X} type={file.sectionType}')
            for symbol in file:
                size = f'{symbol.size:X}' if symbol.size is not None else '???'
                print(f'    symbol {symbol.name:<40} vram={symbol.vram:08X} size={size}')

def main():
    description = "Parses z64.map and produces tables for spimdisasm."

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--game", help="Game to use.", required=True)
    parser.add_argument("--version", help="Version to use.", required=True)
    parser.add_argument("MAPFILE", help="Map file to use.")
    args = parser.parse_args()

    mapFile = mapfile.MapFile()
    mapFile.readMapFile(args.MAPFILE)

    # printMapFile(mapFile)
    # return

    fileLists = collections.defaultdict(list)
    overlays = []
    functions = []

    for segment in mapFile:
        if segment.name == '..dmadata':
            print(f'file table offset: 0x{segment.vrom:X}')

        if segment.name.startswith('..ovl_') and not segment.name.endswith('.bss'):
            overlays.append(segment)

        for file in segment:
            if file.sectionType == '.text':
                functions.extend(file)

            if file.sectionType in ('.text', '.data', '.rodata', '.bss', '.ovl'):
                if segment.name == '..boot' or segment.name == '..boot.bss':
                    fileLists['boot'].append(file)
                elif segment.name == '..code' or segment.name == '..code.bss':
                    fileLists['code'].append(file)
                elif segment.name == '..ovl_file_choose' or segment.name == '..ovl_file_choose.bss':
                    fileLists['ovl_file_choose'].append(file)
                elif segment.name == '..ovl_kaleido_scope' or segment.name == '..ovl_kaleido_scope.bss':
                    fileLists['ovl_kaleido_scope'].append(file)

    outputDir = f'{args.game}/{args.version}/tables'

    for romFile, section in fileLists.items():
        with open(f'{outputDir}/files_{romFile}.csv', 'w') as f:
            offset = 0
            prevFile = None
            for file in section:
                name, ext = os.path.splitext(os.path.basename(file.filepath))
                if ext != '.o':
                    continue

                if '/audio/lib/' in str(file.filepath):
                    name = f'audio_lib_{name}'
                elif '/audio/' in str(file.filepath):
                    name = f'audio_{name}'
                elif name == 'fault.bss':
                    name = 'fault'
                elif name == 'fault_drawer.bss':
                    name = 'fault_drawer'

                if prevFile is None:
                    f.write(f'offset,vram,{file.sectionType}\n')
                elif prevFile.sectionType != file.sectionType:
                    f.write('\n')
                    f.write(f'offset,vram,{file.sectionType}\n')

                if prevFile is not None:
                    offset += file.vram - prevFile.vram
                prevFile = file

                f.write(f'{offset:X},{file.vram:X},{name}\n')

            if prevFile is not None:
                f.write(f'{offset + prevFile.size:X},{prevFile.vram + prevFile.size:X},.end\n')

    with open(f'{outputDir}/file_addresses.csv', 'w') as f:
        f.write('File name,VROM start,VROM end,ROM start,ROM end,Size (VROM),Compressed?,VRAM start,VRAM end,Size (VRAM),bss,type,number\n')
        for overlay in overlays:
            # only file name and VRAM start are used
            f.write(f'{overlay.name[2:]},{overlay.vrom:08X},0,0,0,0,N,{overlay.vram:08X},,,,,\n')

    with open(f'{outputDir}/functions.csv', 'w') as f:
        for symbol in functions:
            f.write(f'{symbol.vram:08X},{symbol.name}\n')

if __name__ == '__main__':
    main()
