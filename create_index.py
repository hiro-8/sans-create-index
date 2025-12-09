import re
import argparse
import fitz
from collections import defaultdict
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from wordfreq import zipf_frequency

# ==========================================================
# メイン処理
# ==========================================================
def main():
    args = parse_args()

    # 語句リストを外部ファイルから読み込む
    global CYBER_TERMS
    CYBER_TERMS = load_cyber_terms("wordlist.txt")

    index = create_index(args.pdf_files, args.max_count)
    output_index_pdf(index, args.output)

# ==========================================================
# argparse: コマンドライン引数
# ==========================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="PDF 索引を作成するツール"
    )

    parser.add_argument(
        "pdf_files",
        nargs="+",
        help="読み込む PDF ファイル（複数指定可）"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="Index.pdf",
        help="出力 PDF ファイル名（デフォルト: Cyber_Index.pdf）"
    )

    parser.add_argument(
        "-m",
        "--max-count",
        type=int,
        default=20,
        help="出現回数の最大値（この数未満だけ索引に残す）"
    )

    return parser.parse_args()


# ==========================================================
# ★ 語句リスト
# ==========================================================
def load_cyber_terms(file_path):
    terms = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            term = line.strip()
            if term:
                terms.append(term.lower())
    return terms


# ==========================================================
# PDF テキスト抽出（ページごと）
# ==========================================================
def extract_text_fully(pdf_path):
    text_pages = []
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text("text")  # すべてのレイヤーのテキストを取得
        text_pages.append(text)
    return text_pages


# ==========================================================
# 索引を作成（熟語優先 + 単語抽出）
# ==========================================================
def create_index(pdf_files, max_count):
    index = defaultdict(lambda: defaultdict(list))

    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        pdf_name = pdf_file

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text").lower()

            # --- 熟語マッチ ---
            for phrase in CYBER_TERMS:
                pattern = re.escape(phrase)
                matches = re.findall(pattern, text)
                if matches:
                    index[phrase][pdf_name].append(page_number)
                text = re.sub(pattern, " ", text)

            # --- 単語マッチ ---
            words = re.findall(r"[a-zA-Z]+", text)

            for word in words:
                # 1. サイバー用語リストにある → 無条件で採用
                if word in CYBER_TERMS:
                    index[word][pdf_name].append(page_number)
                    continue

                # 2. 熟語に含まれず単語として来た場合
                #    → 英語辞書に載る一般単語は除外
                if is_common_english(word):
                    continue
                
                # 3. 一般的でない英単語 → 追加する！！
                index[word][pdf_name].append(page_number)

        doc.close()

    # --- 出現回数フィルタリング（PDFごとページ数の合計で比較） ---
    filtered = {}
    for term, pdf_pages in index.items():
        total = sum(len(pages) for pages in pdf_pages.values())
        if 3 < total and total < max_count:
            filtered[term] = pdf_pages

    return filtered


# ==========================================================
# PDF 出力
# ==========================================================
def output_index_pdf(index_data, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    body_style = styles["BodyText"]
    title = output_pdf.split('.')
    story.append(Paragraph(title[0], title_style))
    story.append(Spacer(1, 20))

    for term in sorted(index_data.keys()):
        # 用語タイトル
        story.append(Paragraph(f"<b>{term}</b>", body_style))
        story.append(Spacer(1, 6))

        # PDF名ごとに改行してリスト表示
        for pdf_name, pages in index_data[term].items():
            unique_sorted = sorted(set(pages))
            page_str = ",".join(str(p-2) for p in unique_sorted)
            line = f"&nbsp;&nbsp;{pdf_name} : {page_str}"
            story.append(Paragraph(line, body_style))

        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"PDF 出力完了：{output_pdf}")

# ==========================================================
#    Zipf frequency が 4.0 以上の単語は一般的な英単語とみなして除外する。
#    3.5〜4.0 は微妙だが、サイバー用語はほぼ 2.0 以下なので問題なし。
# ==========================================================
def is_common_english(word):
    return zipf_frequency(word, 'en') >= 2.0


if __name__ == "__main__":
    main()
