import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;

public class ExportDecompiled extends GhidraScript {
    @Override
    public void run() throws Exception {
        File outputFile = new File("C:\\Users\\Aycher\\Documents\\Default Project\\analysis\\src\\decompiled.c");
        PrintWriter writer = new PrintWriter(new FileWriter(outputFile));
        
        FunctionManager fm = currentProgram.getFunctionManager();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        
        writer.println("// Decompiled from: " + currentProgram.getName());
        writer.println("// Total functions: " + fm.getFunctionCount());
        writer.println();
        
        FunctionIterator functions = fm.getFunctions(true);
        int count = 0;
        int maxFns = 60;
        
        while (functions.hasNext() && count < maxFns) {
            Function function = functions.next();
            String name = function.getName();
            if (name.startsWith("_") || name.startsWith("FUN_") || name.length() < 20) {
                DecompileResults results = decompiler.decompileFunction(function, 60, getMonitor());
                if (results.decompileCompleted()) {
                    writer.println("// ===== " + name + " @ " + function.getEntryPoint() + " =====");
                    writer.println(results.getDecompiledFunction().getC());
                    writer.println();
                    count++;
                }
            }
        }
        
        writer.close();
        decompiler.closeProgram();
        println("Decompiled " + count + " functions to " + outputFile.getAbsolutePath());
    }
}
