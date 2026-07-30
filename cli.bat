@echo off
setlocal
title AKO Visual Design Agent v1.2

if not "%~1"=="" goto :run

REM No arguments: launch interactive wizard
python "%~dp0config_wizard.py"
goto :done

:run
where AKO_visual_design_agent.exe >nul 2>nul
if %errorlevel% equ 0 (
    AKO_visual_design_agent.exe %*
    goto :done
)
if exist "%~dp0dist\AKO_visual_design_agent.exe" (
    "%~dp0dist\AKO_visual_design_agent.exe" %*
    goto :done
)
python "%~dp0main.py" %*

:done
python -c "import msvcrt; print(); print('  \u6309\u4efb\u610f\u952e\u9000\u51fa...'); msvcrt.getch()"
endlocal
exit /b
