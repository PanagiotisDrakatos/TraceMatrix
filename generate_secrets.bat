@echo off
REM Script to generate random secrets for .env file

echo Generating random secrets...
echo.

REM Generate a random string for SearXNG (32 chars)
set "chars=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
set "searxng_secret="
for /L %%i in (1,1,32) do (
    set /a "rand=!random! %% 62"
    for %%j in (!rand!) do set "searxng_secret=!searxng_secret!!chars:~%%j,1!"
)

echo Generated SearXNG Secret Key:
powershell -Command "$bytes = [byte[]]::new(32); (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); -join ($bytes | ForEach-Object { '{0:x2}' -f $_ })"
echo.

echo Generated OpenSearch Password:
powershell -Command "$bytes = [byte[]]::new(16); (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); -join ($bytes | ForEach-Object { [char](33 + ($_ %% 94)) })"
echo.

echo Copy these values to your .env file!
echo.
pause

