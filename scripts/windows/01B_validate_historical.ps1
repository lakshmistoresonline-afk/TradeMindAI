# TradeMind AI Historical Data Validation Gate
# Step 1B: Validation Only

$ErrorActionPreference = "Stop"

# Activate venv
$VENV_PATH = "$PSScriptRoot/../../.venv"
if (Test-Path "$VENV_PATH/Scripts/Activate.ps1") {
    . "$VENV_PATH/Scripts/Activate.ps1"
}

python -m scripts.universe.validate_historical
exit $LASTEXITCODE
