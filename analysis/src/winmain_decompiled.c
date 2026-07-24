rizin.exe : WARNING: bin_file_strings: search interval size (0x1030a00) exceeds max region size (0xa00000), skipping 
it.
At line:10 char:1
+ & "$src\rizin.exe" -q -c "s 0x140001020; af; pdc 80" $target 2>&1 | O ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (WARNING: bin_fi...), skipping it.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
WARNING: bin_file_strings: search interval size (0x172ba00) exceeds max region size (0xa00000), skipping it.
WARNING: bin_file_strings: search interval size (0xb11d600) exceeds max region size (0xa00000), skipping it.
WARNING: bin_file_strings: search interval size (0x1030a00) exceeds max region size (0xa00000), skipping it.
WARNING: bin_file_strings: search interval size (0x172ba00) exceeds max region size (0xa00000), skipping it.
WARNING: bin_file_strings: search interval size (0xb11d600) exceeds max region size (0xa00000), skipping it.
ERROR: Command 'pdc' does not exist.
ERROR: Displaying the help of command 'pd'.

ERROR: [36mUsage: [0m[37mpd[0m[?][33m[0m   [32m# Print Disassembly[0m
??? [37mpd[0m[jqt][33m [<n_instrs>]  [32m# Disassemble N instructions (can be negative)[0m
??? [37mpda[0m[jq=][33m              [32m# Disassemble all possible opcodes (byte per byte)[0m
??? [37mpdb[0m[jJ][33m               [32m# Disassemble basic block[0m
??? [37mpdC[33m [<n_instrs>]      [32m# Prints the comments found in N instructions[0m
??? [37mpde[0m[jqQ][33m [<n_instrs>] [32m# Disassemble N instructions following execution flow from current PC[0m
??? [37mpdf[0m[js][33m               [32m# Disassemble a function[0m
??? [37mpdJ[0m[?][33m [<n_instrs>]   [32m# Disassemble N instructions as json containing the printed text[0m
??? [37mpdk[33m                   [32m# Disassemble all methods of a class[0m
??? [37mpdl[0m[j][33m [<n_instrs>]   [32m# Disassemble N instructions and prints its sizes[0m
??? [37mpdp[0m[jq][33m [<limit>]     [32m# Disassemble instructions and follows pointers to read ropchains[0m
??? [37mpdr[0m[j.][33m               [32m# Disassemble recursively across the function graph[0m
??? [37mpdR[0m[jq][33m               [32m# Disassemble recursively the block size bytes without analyzing 
functions[0m
??? [37mpds[0m[fb][33m               [32m# Summarize N bytes or current block or a function (strings, calls, 
jumps, refs)[0m
??? [37mpdg[0m[?][33m                [32m# Native Ghidra decompiler and Sleigh Disassembler plugin[0m
