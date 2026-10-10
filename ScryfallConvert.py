import json
import os
from collections import defaultdict

# パスは環境に併せて変更してください
INPUT_FILE = r"E:\Download\all-cards-yyyymmddhhmmss.jsonl\all-cards-yyyymmddhhmmss.jsonl"
OUTPUT_DIR = r"E:\Download\mtg_format_color_split"

# 出力したいフォーマットを記載してください
TARGET_FORMATS = ['standard', 'pioneer', 'historic', 'timeless', 'commander']

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_color_category(card):
    """カードの色を判定（両面カードも対応しています）"""
    colors = card.get('colors')
    # 両面カード等でトップレベルにcolorsがない場合、表面の色または固有色を参照する
    if colors is None:
        if 'card_faces' in card and 'colors' in card['card_faces'][0]:
            colors = card['card_faces'][0]['colors']
        else:
            colors = card.get('color_identity', [])

    if len(colors) == 0:
        return 'colorless'
    elif len(colors) > 1:
        return 'multicolor'
    else:
        mapping = {'W': 'white', 'U': 'blue', 'B': 'black', 'R': 'red', 'G': 'green'}
        return mapping.get(colors[0], 'other')

def transform_to_text(card):
    """AIが読み取りやすいテキスト形式に整形（両面カードも対応しています）"""
    name_en = card.get('name', 'Unknown')
    name_ja = card.get('printed_name', '')
    display_name = f"{name_en} ({name_ja})" if name_ja else name_en
    
    set_name = card.get('set_name', 'Unknown')
    type_line = card.get('type_line', '')

    # 両面カード・分割カードの場合は各面のテキストを結合する
    if 'card_faces' in card and 'oracle_text' not in card:
        faces_text = []
        mana_costs = []
        for face in card['card_faces']:
            f_cost = face.get('mana_cost', '')
            if f_cost:
                mana_costs.append(f_cost)
            f_text = face.get('oracle_text', '').replace('\n', ' ')
            faces_text.append(f"[{face.get('name', '')}] {f_text}")
        mana_cost = " // ".join(mana_costs)
        oracle_text = " // ".join(faces_text)
    else:
        mana_cost = card.get('mana_cost', '')
        oracle_text = card.get('oracle_text', 'No text').replace('\n', ' ')
    
    return f"NAME: {display_name} | COST: {mana_cost} | TYPE: {type_line} | TEXT: {oracle_text} | SET: {set_name}\n"

print("フォーマット × 色 別の詳細分割を開始します...")

# ファイル開閉の負荷を減らすため、メモリ上にデータを溜める辞書を用意する
buffers = defaultdict(list)
# 再録カードの重複を防ぐためのセットを置く
seen_cards = set()

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    for count, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
            
        card = json.loads(line)
        
        # 英語版のみを抽出する
        if card.get('lang') != 'en':
            continue
            
        # 同名カードの重複をスキップ（再録やプロモ違いを除外）する
        card_name = card.get('name')
        if card_name in seen_cards:
            continue
        seen_cards.add(card_name)
            
        legalities = card.get('legalities', {})
        color_cat = get_color_category(card)
        text_data = transform_to_text(card)
        
        # 該当するフォーマットのバッファに追加する
        for fmt in TARGET_FORMATS:
            if legalities.get(fmt) == 'legal':
                file_name = f"{fmt}_{color_cat}.txt"
                buffers[file_name].append(text_data)
        
        if count % 50000 == 0:
            print(f"{count}行 処理中... (ユニークなカード総数: {len(seen_cards)}枚)")

# まとめてファイルに書き出す（上書きモード 'w' で以前のゴミデータをリセット）
print("ファイルへ書き出しています...")
for file_name, lines in buffers.items():
    file_path = os.path.join(OUTPUT_DIR, file_name)
    with open(file_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(lines)

print(f"完了！ {OUTPUT_DIR} 内のファイルをNotebookLMにアップロードしてください。")
