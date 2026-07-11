@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  NewBacktesting — Full Run Script
::  Runs all unit tests in order, then batch-backtests every
::  strategy against every Hyperliquid CSV file.
:: ============================================================

:: Keep the window open if anything goes wrong early
:: by routing errors through :die instead of bare exit

:: --- Configuration -------------------------------------------
set CONDA_ROOT=C:\Users\andre\anaconda3
set CONDA_ENV=backtesting
set PROJECT_DIR=%~dp0
:: Strip trailing backslash
if "%PROJECT_DIR:~-1%"=="\" set PROJECT_DIR=%PROJECT_DIR:~0,-1%

set SRC_DIR=%PROJECT_DIR%\src
set DATA_DIR=%PROJECT_DIR%\data\Hyperliquid
set STRATEGIES_DIR=%PROJECT_DIR%\strategies
set RESULTS_ROOT=D:\Results
set LOG_DIR=D:\Results\logs

:: ============================================================
echo.
echo ============================================================
echo  NewBacktesting Full Run
echo  %date%  %time%
echo  Conda   : %CONDA_ROOT%
echo  Env     : %CONDA_ENV%
echo  Project : %PROJECT_DIR%
echo ============================================================
echo.

:: --- Initialize conda for cmd --------------------------------
echo [SETUP] Initializing conda...
if not exist "%CONDA_ROOT%\Scripts\activate.bat" (
    echo [ERROR] Cannot find conda at: %CONDA_ROOT%\Scripts\activate.bat
    echo         Edit CONDA_ROOT at the top of this script.
    goto :die
)

call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ROOT%"
if errorlevel 1 goto :conda_fail

echo [SETUP] Activating environment: %CONDA_ENV%
call conda activate %CONDA_ENV%
if errorlevel 1 goto :conda_fail

echo [SETUP] Active environment:
call conda info --envs | findstr /C:"*"
echo.
goto :conda_ok

:conda_fail
echo [ERROR] Could not activate conda env "%CONDA_ENV%"
echo         Make sure you ran:  conda create -n backtesting python=3.11
goto :die

:conda_ok

:: --- Python path setup ---------------------------------------
:: Paths are injected by batch_runner.py itself at startup using
:: __file__ as anchor — no PYTHONPATH override needed.

:: --- Results / log dirs --------------------------------------
if not exist "%RESULTS_ROOT%" mkdir "%RESULTS_ROOT%"
if not exist "%LOG_DIR%"      mkdir "%LOG_DIR%"

:: Build a clean timestamp (strip spaces from time for pre-10am hours)
set "RAW_TIME=%time: =0%"
set "TS=%date:~10,4%%date:~4,2%%date:~7,2%_%RAW_TIME:~0,2%%RAW_TIME:~3,2%%RAW_TIME:~6,2%"
set RESULTS_DIR=%RESULTS_ROOT%\batch_%TS%
set LOG_FILE=%LOG_DIR%\run_%TS%.log

echo Run started: %date% %time% > "%LOG_FILE%"
echo Results dir: %RESULTS_DIR%  >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

echo [INFO] Results  : %RESULTS_DIR%
echo [INFO] Log file : %LOG_FILE%
echo.

:: ============================================================
:: PHASE 1 — UNIT TESTS (in dependency order)
:: ============================================================
echo ============================================================
echo  PHASE 1 ^| Unit Tests
echo ============================================================
echo.

set TEST_PASS=0
set TEST_FAIL=0

call :run_test "1/4" "test_default_paths.py"
call :run_test "2/4" "test_strategy_migration.py"
call :run_test "3/4" "test_new_strategy_folders.py"
call :run_test "4/4" "test_batch_runner.py"

echo.
echo --- Test summary: %TEST_PASS% passed  /  %TEST_FAIL% failed ---
echo.

:: ============================================================
:: PHASE 2 — BATCH BACKTEST
:: ============================================================
echo ============================================================
echo  PHASE 2 ^| Batch Backtest
echo  Strategies : %STRATEGIES_DIR%
echo  Data       : %DATA_DIR%
echo  Workers    : 6
echo  Output     : %RESULTS_DIR%
echo ============================================================
echo.

python "%SRC_DIR%\backtest\batch_runner.py" ^
    --data-dir       "%DATA_DIR%"       ^
    --strategies-dir "%STRATEGIES_DIR%" ^
    --results-dir    "%RESULTS_DIR%"    ^
    --max-workers    6                  ^
    --recursive                         ^
    --manifest       "%RESULTS_DIR%\batch_manifest.json"

if errorlevel 1 (
    echo.
    echo [ERROR] Batch run exited with errors. See log: %LOG_FILE%
) else (
    echo.
    echo [OK] Batch run complete.
    echo      Results  : %RESULTS_DIR%
    echo      Manifest : %RESULTS_DIR%\batch_manifest.json
)

:: ============================================================
:: DONE
:: ============================================================
echo.
echo ============================================================
echo  Finished: %date%  %time%
echo  Tests   : %TEST_PASS% passed  /  %TEST_FAIL% failed
echo  Log     : %LOG_FILE%
echo ============================================================
echo.
goto :end

:: ============================================================
:: Subroutine — run a single pytest file
:: Usage:  call :run_test "N/4" "filename.py"
:: ============================================================
:run_test
set _NUM=%~1
set _FILE=%~2
echo [TEST %_NUM%] %_FILE%
echo. >> "%LOG_FILE%"
echo [TEST %_NUM%] %_FILE% >> "%LOG_FILE%"

python -m pytest "%PROJECT_DIR%\tests\%_FILE%" -v >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo   [FAIL] — check log for details
    set /a TEST_FAIL+=1
) else (
    echo   [PASS]
    set /a TEST_PASS+=1
)
goto :eof

:: ============================================================
:: Error exit — always pause so window stays open
:: ============================================================
:die
echo.
echo Script cannot continue. Fix the error above and re-run.
echo.
pause
exit /b 1

:end
pause
endlocal
