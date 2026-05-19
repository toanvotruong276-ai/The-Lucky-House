#!/usr/bin/env bash
# Build script cho Render.com
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Seed dữ liệu mẫu (bỏ qua lỗi nếu đã seed rồi)
python seed.py || echo "[WARN] Seed skipped or failed - may already exist"
