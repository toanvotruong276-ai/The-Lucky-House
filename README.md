# Python Workspace

Moi truong nay dung Python 3.13 voi virtual environment rieng tai `.venv`.

## Lenh thuong dung

Kich hoat moi truong:

```powershell
.\.venv\Scripts\Activate.ps1
```

Chay chuong trinh mau:

```powershell
python src\main.py
```

Chay test:

```powershell
pytest
```

Kiem tra va format code:

```powershell
ruff check .
black .
```

Them package moi:

```powershell
pip install ten-package
```

Neu dung VS Code, mo thu muc nay va chon interpreter `.venv\Scripts\python.exe`.

