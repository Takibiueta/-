# Facebook動画ダウンローダー

Facebookにアップロードされている動画を、URLを指定するだけでMP4としてダウンロードできるツールです。
中身は動画ダウンロードの定番ライブラリ [yt-dlp](https://github.com/yt-dlp/yt-dlp) を使っています。

> **⚠️ 利用上の注意**
> 自分がアップロードした動画、または権利者から許可を得ている動画のダウンロードにのみ使用してください。
> 他人の動画を無断で保存・再配布することは、著作権法やFacebookの利用規約に違反する可能性があります。

---

## 1. 事前準備(最初の1回だけ)

### 必要なもの

- **Python 3.8以上** … [python.org](https://www.python.org/downloads/) からインストール(Windowsの場合、インストール時に「Add Python to PATH」に必ずチェック)
- **ffmpeg**(推奨)… 高画質動画は映像と音声が別ファイルになっているため、結合に必要です

### インストール手順

ターミナル(Windowsなら「コマンドプロンプト」または「PowerShell」)で以下を実行:

```bash
# yt-dlp のインストール
pip3 install yt-dlp

# ffmpeg のインストール
# Mac (Homebrew):
brew install ffmpeg
# Windows (winget):
winget install ffmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg
```

---

## 2. 基本の使い方

### ① ダウンロードしたい動画のURLをコピーする

Facebookで動画を開き、以下のいずれかの方法でURLを取得します。

- 動画の右上「…」メニュー →「リンクをコピー」
- ブラウザのアドレスバーのURLをコピー

URLの例:
- `https://www.facebook.com/watch?v=1234567890`
- `https://www.facebook.com/ユーザー名/videos/1234567890/`
- `https://fb.watch/xxxxxxxx/`(短縮URL)
- `https://www.facebook.com/reel/1234567890`(リール)

### ② コマンドを実行する

このフォルダ(`facebook-video-downloader`)に移動して:

```bash
python3 fb_download.py "コピーしたURL"
```

例:

```bash
python3 fb_download.py "https://www.facebook.com/watch?v=1234567890"
```

`downloads` フォルダに動画が保存されます。

> **URLは必ず `"` (ダブルクォート)で囲んでください。** URLに `?` や `&` が含まれていると、囲まないとエラーになります。

---

## 3. よく使うオプション

| やりたいこと | コマンド例 |
|---|---|
| 保存先を変える | `python3 fb_download.py -o ~/Desktop/videos "URL"` |
| 複数の動画をまとめて | `python3 fb_download.py "URL1" "URL2" "URL3"` |
| 音声だけ(MP3)保存 | `python3 fb_download.py --audio-only "URL"` |
| 画質の一覧を確認 | `python3 fb_download.py --list-formats "URL"` |

---

## 4. 非公開・友達限定の動画をダウンロードする場合

自分のアカウントでログインしないと見られない動画(自分の投稿・友達限定・グループ内の動画など)は、
**ブラウザのログイン情報(Cookie)を借りる**ことでダウンロードできます。

普段Facebookにログインしているブラウザを指定してください:

```bash
# Chromeでログインしている場合
python3 fb_download.py --browser chrome "URL"

# Firefoxの場合
python3 fb_download.py --browser firefox "URL"

# Edge / Safari / Brave も指定可能
python3 fb_download.py --browser edge "URL"
```

> **注意(Chrome/Edgeユーザー)**: ブラウザを起動したままだとCookieの読み取りに失敗することがあります。
> エラーが出る場合は、一度ブラウザを完全に終了してから実行してください。
> それでもだめな場合は、ブラウザ拡張機能「Get cookies.txt LOCALLY」などでCookieをファイルに書き出し、
> `python3 fb_download.py --cookies cookies.txt "URL"` のように指定する方法もあります。

---

## 5. よくあるトラブルと対処法

| 症状 | 対処法 |
|---|---|
| `login required` / `This video is unavailable` と出る | 非公開動画の可能性 → 上記の `--browser` オプションを使う |
| 映像と音声が別々に保存される / 結合エラー | ffmpegが未インストール → 手順1でffmpegを入れる |
| `pip3: command not found` | Pythonが未インストール、またはPATH未設定 → Pythonを入れ直す(Windowsは「Add to PATH」にチェック) |
| 以前は動いたのに急に失敗するようになった | Facebook側の仕様変更 → `pip3 install -U yt-dlp` でyt-dlpを最新版に更新 |
| ダウンロードが途中で止まる | 再実行すればOK(ダウンロード済み部分から再開されます) |

---

## 6. ファイル構成

```
facebook-video-downloader/
├── fb_download.py    # ダウンロードスクリプト本体
├── README.md         # このファイル
└── requirements.txt  # 必要なPythonライブラリ一覧
```
