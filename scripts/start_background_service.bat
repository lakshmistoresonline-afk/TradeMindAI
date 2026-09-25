@echo off
title TradeMind AI 15-Min Background Service
cd /d "G:\TradeMindAI"
echo ==========================================================================
echo  Starting TradeMind AI 15-Minute Background Market Data & Signal Updater...
echo ==========================================================================
node scripts/windows_background_updater.js
pause
