# sans create index
```
tree ./                                             
./
├── create_index.py
├── FOR509 - Book 1.pdf
├── FOR509 - Book 2.pdf
├── FOR509 - Book 3.pdf
├── FOR509 - Book 4.pdf
├── FOR509 - Book 5.pdf
└── wordlist.txt
```
```
┌──(kali㉿kali)-[~/Desktop/FOR509/index]
└─$ python3 create_index.py -h                                                                                                           
usage: create_index.py [-h] [-o OUTPUT] [-m MAX_COUNT] pdf_files [pdf_files ...]

PDF 索引を作成するツール

positional arguments:
  pdf_files             読み込む PDF ファイル（複数指定可）

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   出力 PDF ファイル名（デフォルト: Cyber_Index.pdf）
  -m, --max-count MAX_COUNT
                        出現回数の最大値（この数未満だけ索引に残す）
```

```
┌──(kali㉿kali)-[~/Desktop/FOR509/index]
└─$ python3 create_index.py *.pdf -o for509_index.pdf                                                                                    
PDF 出力完了：for509_index.pdf
```
