@echo off
title TradeMind AI Background Updater Log Viewer
cd /d "G:\TradeMindAI"
echo ==========================================================================
echo  TradeMind AI: Live Background Updater Status & Log Viewer
echo ==========================================================================
node scripts/check_background_status.js
pause
