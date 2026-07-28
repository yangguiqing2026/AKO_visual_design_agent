@echo off
chcp 65001 >nul
:: AKO_visual_design_agent CLI 快捷启动脚本
:: 作者：AKO_studio
:: 版本：v1.2

setlocal

title AKO Visual Design Agent CLI

:: 如果已安装到系统 PATH，直接用
where AKO_visual_design_agent.exe >nul 2>nul
if %errorlevel% equ 0 (
    echo ============================================================
    echo  AKO Visual Design Agent v1.2.0
    echo  四层架构: Perceptor → Planner → Reviewer → Producer
    echo ============================================================
    echo.
    AKO_visual_design_agent.exe %*
    goto :end
)

:: 如果有本地 dist
if exist "%~dp0dist\AKO_visual_design_agent.exe" (
    echo ============================================================
    echo  AKO Visual Design Agent v1.2.0 (开发模式)
    echo ============================================================
    echo.
    "%~dp0dist\AKO_visual_design_agent.exe" %*
    goto :end
)

:: Python 源码模式
echo ============================================================
echo  AKO Visual Design Agent v1.2.0 (源码模式)
echo ============================================================
echo.
python "%~dp0main.py" %*
goto :end

:end
endlocal