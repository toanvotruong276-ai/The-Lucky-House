#!/usr/bin/env bash
# Build script cho Render.com
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Seed dữ liệu mẫu nếu chưa có (chỉ chạy lần đầu)
python seed.py
