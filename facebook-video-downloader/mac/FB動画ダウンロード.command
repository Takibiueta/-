#!/bin/bash
# Facebook動画ダウンローダー(ダブルクリック版・Mac用)
#
# 使い方:
#   1. Facebookで動画のURLをコピー(⌘C)
#   2. このファイルをダブルクリック
#   → 外部SSD「CASTING」内の Facebook フォルダに保存されます
#     (SSDが接続されていない場合はデスクトップに保存されます)

SSD_NAME="CASTING"
SSD_DIR="/Volumes/$SSD_NAME/Facebook"

if [ -d "/Volumes/$SSD_NAME" ]; then
  mkdir -p "$SSD_DIR"
  SAVE_DIR="$SSD_DIR"
  echo "保存先: 外部SSD「$SSD_NAME」の Facebook フォルダ"
else
  SAVE_DIR="$HOME/Desktop"
  echo "外部SSD「$SSD_NAME」が見つからないため、デスクトップに保存します。"
  echo "(SSDに保存したい場合は接続してからやり直してください)"
fi

cd "$SAVE_DIR" || exit 1

# yt-dlp の場所を探す(pipx版を優先)
if [ -x "$HOME/.local/bin/yt-dlp" ]; then
  YTDLP="$HOME/.local/bin/yt-dlp"
elif command -v yt-dlp >/dev/null 2>&1; then
  YTDLP="$(command -v yt-dlp)"
else
  echo "エラー: yt-dlp が見つかりません。"
  echo '次のコマンドでインストールしてください:'
  echo '    brew install pipx ffmpeg'
  echo '    pipx install "yt-dlp[default,curl-cffi]"'
  read -r -p "Enterキーで閉じます..."
  exit 1
fi

# クリップボードにFacebookのURLがあればそれを使い、なければ入力してもらう
URL="$(pbpaste)"
case "$URL" in
  http*facebook.com*|http*fb.watch*)
    echo "コピーされているURLを使います:"
    echo "  $URL"
    ;;
  *)
    echo "FacebookのURLがコピーされていません。"
    printf "動画のURLをここに貼り付けてEnterを押してください: "
    read -r URL
    ;;
esac

if [ -z "$URL" ]; then
  echo "URLが入力されませんでした。"
  read -r -p "Enterキーで閉じます..."
  exit 1
fi

echo ""
echo "=== ダウンロード開始(保存先: $SAVE_DIR)==="
"$YTDLP" --impersonate chrome --cookies-from-browser chrome -P "$SAVE_DIR" "$URL"
STATUS=$?

echo ""
if [ $STATUS -eq 0 ]; then
  echo "✅ 完了! $SAVE_DIR に動画が保存されました。"
else
  echo "❌ 失敗しました。上のエラーメッセージを確認してください。"
  echo "   ヒント: Chromeを完全に終了(⌘Q)してから再実行すると直ることがあります。"
fi
read -r -p "Enterキーでこのウィンドウを閉じます..."
