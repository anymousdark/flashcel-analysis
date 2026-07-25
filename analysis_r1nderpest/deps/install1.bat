echo Installing Python...
python.exe /quiet /PrependPath=1 /InstallAllUsers=1
echo Installing Visual C++ Build Tools
buildtools.exe --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools