@echo on
:: this is a nasty hack, and should not be needed

call deactivate
call C:\Miniconda\envs\ipyradiant\Scripts\activate
call conda info --json
call doit -n4 release
call doit release || goto :error

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit 1

