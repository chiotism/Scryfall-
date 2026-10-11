# Scryfallのバルクデータをテキスト形式に変換するやつ

## 動作環境

Python 3.x（外部ライブラリのインストールは不要です）

## 実行手順

1. データの準備
ScryfallのBulk Dataページ（https://scryfall.com/docs/api/bulk-data）から、カードデータのファイル（All Cards または Default Cards 等）をダウンロードします。

2. パスの設定
スクリプト（`convert_mtg.py`）を開き、以下の変数を自身の環境に合わせて書き換えます。

```python
INPUT_FILE = r"ダウンロードしたファイルのパス"
OUTPUT_DIR = r"出力先フォルダのパス"
TARGET_FORMATS = ['standard', 'pioneer', 'historic', 'timeless', 'commander']

