rem
rem
rem You should be inside RHTEST directory to start this
rem 
rem

set RHTEST_HOME=%cd%
set PYTHONPATH=%RHTEST_HOME%\lib;%RHTEST_HOME%\lib\supports;%RHTEST_HOME%\testmodules;%PYTHONPATH%
echo %cd%
cd %RHTEST_HOME%
git pull
rem set RHTEST_ARGS= -R -G 

set RHTEST_DEBUG=1
set EXISTING_INSTANCE_TAG=QE_mzimen-dev
python bin\launcher.py -A %EXISTING_INSTANCE_TAG% -i %TESTRUN_ID% -d

exit



