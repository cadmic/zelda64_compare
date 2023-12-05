#! /usr/bin/env python3

import glob
import os
import re
import sys

UNKNOWN_FUNC_RE = re.compile(r"func_([0-9A-F]{8})_unknown")

def find_functions(cpm_filename, test_filename, banned_funcs):
    basename = os.path.basename(test_filename)
    if not os.path.exists(cpm_filename):
        return

    cpm_funcs = []
    with open(cpm_filename) as f:
        for line in f:
            if line.startswith("glabel "):
                func_name = line.split()[1]
                if not func_name.startswith("D_"):
                    cpm_funcs.append(line.split()[1])

    test_funcs = []
    with open(test_filename) as f:
        for line in f:
            if line.startswith("glabel "):
                func_name = line.split()[1]
                if not func_name.startswith("D_") and func_name not in banned_funcs:
                    test_funcs.append(func_name)

    if len(cpm_funcs) != len(test_funcs):
        print(f"{basename}: different number of functions cpm={len(cpm_funcs)} test={len(test_funcs)}", file=sys.stderr)
        return

    for cpm_func, test_func in zip(cpm_funcs, test_funcs):
        match = UNKNOWN_FUNC_RE.fullmatch(cpm_func)
        if not match:
            continue
        cpm_addr = int(match.group(1), 16)
        print('{0:08X},{1}'.format(cpm_addr, test_func))

def find_code_functions():
    banned_funcs = [
        'AudioDebug_SetInput',
        'AudioDebug_ToStringBinary',
        'AudioDebug_Draw',
        'AudioDebug_ProcessInput_SndCont',
        'AudioDebug_ProcessInput_IntInfo',
        'AudioDebug_ProcessInput_ScrPrt',
        'AudioDebug_ProcessInput_SfxSwap',
        'AudioDebug_ProcessInput_SubTrackInfo',
        'AudioDebug_ProcessInput_HeapInfo',
        'AudioDebug_ProcessInput_BlkChgBgm',
        'AudioDebug_ProcessInput_OcaTest',
        'AudioDebug_ProcessInput_SfxParamChg',
        'AudioDebug_ScrPrt',
        'AudioDebug_ProcessInput',
        'GameState_FaultPrint',
        'GameState_Alloc',
        'GameState_GetArenaSize',
        'Graph_FaultClient',
        'Graph_DisassembleUCode',
        'Graph_UCodeFaultClient',
        'Graph_OpenDisps',
        'Graph_CloseDisps',
        'GameAlloc_MallocDebug',
        'SystemArena_CheckPointer',
        'SystemArena_MallocDebug',
        'SystemArena_MallocRDebug',
        'SystemArena_ReallocDebug',
        'SystemArena_FreeDebug',
        'SystemArena_Display',
        'Main_LogSystemHeap',
        'ZeldaArena_CheckPointer',
        'ZeldaArena_MallocDebug',
        'ZeldaArena_MallocRDebug',
        'ZeldaArena_ReallocDebug',
        'ZeldaArena_FreeDebug',
        'ZeldaArena_Display',
        'func_800F3054',
        'func_8005B198',
        'func_800D31F0',
        'Cutscene_DrawDebugInfo',
        'Environment_PrintDebugInfo',
        'Message_DrawDebugVariableChanged',
        'Message_DrawDebugText',
        'ViMode_LogPrint',
    ]

    for basename in sorted(os.listdir("oot/test/asm/text/code")):
        if not basename.endswith(".s"):
            continue

        cpm_filename = os.path.join("oot/cpm/asm/text/code", basename)
        test_filename = os.path.join("oot/test/asm/text/code", basename)

        find_functions(cpm_filename, test_filename, banned_funcs)

def find_overlay_functions():
    banned_funcs = [
        'DemoDu_CsAfterGanon_Reset',
        'DemoDu_CsAfterGanon_CheckIfShouldReset',
        'DemoGj_DoNothing1',
        'DemoGj_DoNothing2',
        'DemoGj_DoNothing3',
        'func_80984C68',
        'func_80984C8C',
        'func_8098E530',
        'func_8098E554',
        'ElfMsg_Draw',
        'ElfMsg2_Draw',
        'func_80AB11EC',
        'func_80AB1210',
        'func_80AE7358',
        'func_80AE73D8',
        'func_80AEB1D8',
        'func_80AEB220',
        'func_80AF0050',
        'func_80AF26AC',
        'func_80AF26D0',
        'EnSyatekiMan_SetBgm',
        'EnXc_NoCutscenePlaying',
        'func_80B3C820',
        'func_80B3C888',
        'ConsoleLogo_PrintBuildInfo',
        'func_8084FCAC', # player debug mode
    ]

    for test_filename in sorted(glob.glob("oot/test/asm/text/ovl_*/*")):
        basename = os.path.basename(test_filename)
        cpm_filename = test_filename.replace("oot/test", "oot/cpm")

        find_functions(cpm_filename, test_filename, banned_funcs)

if __name__ == '__main__':
    find_code_functions()
    find_overlay_functions()
