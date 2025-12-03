#!/usr/bin/env bash
# Render.com build script

set -o errexit

pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
