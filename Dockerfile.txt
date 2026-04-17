FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のファイルをコピー
COPY requirements.txt .

# 必要なパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー (main.py と models フォルダが含まれる)
COPY . .

# Renderが割り当てた環境変数PORTを利用してUvicornを起動
# (デフォルトはポート8000、ホストは0.0.0.0で外部アクセス許可)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
