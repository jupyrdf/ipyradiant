@echo on
:: this is a nasty hack, and should not be needed, but the env isn't _quite_ right

set SKIP_PREFLIGHT=true

call deactivate
call C:\Miniconda\envs\ipyradiant-base\Scripts\activate
call doit -n4 release
call doit release || goto :error

goto :EOF

:error
echo Failed with error #%errorlevel%.
exit 1

