@echo off
set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%

set GHIDRA_DIR=C:\Users\Aycher\Documents\Default Project\analysis\tools\ghidra11\ghidra_11.1.2_PUBLIC
set TARGET=C:\Users\Aycher\Documents\Default Project\analysis\exe\Dark Pro Premium.exe
set PROJ_DIR=C:\Users\Aycher\Documents\Default Project\analysis\tools\ghidra_project
set SCRIPT_DIR=%GHIDRA_DIR%\Ghidra\Features\Base\ghidra_scripts
set OUT=C:\Users\Aycher\Documents\Default Project\analysis\src

call "%GHIDRA_DIR%\support\analyzeHeadless.bat" "%PROJ_DIR%" DarkPro -import "%TARGET%" -scriptPath "%SCRIPT_DIR%" -postScript ExportDecompiled.java -deleteProject
