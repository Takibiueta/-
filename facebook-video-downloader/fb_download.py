#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook動画ダウンローダー

Facebookにアップロードされている動画のURLを指定して、MP4としてダウンロードするツール。

使い方(基本):
    python3 fb_download.py "https://www.facebook.com/watch?v=XXXXXXXXXX"

使い方(非公開・友達限定の動画 = 自分のブラウザのログイン情報を利用):
    python3 fb_download.py --browser chrome "https://www.facebook.com/..."

詳しくは同じフォルダの README.md を参照してください。

注意: ダウンロードは自分がアップロードした動画や、権利者から許可を得ている
動画のみに使用してください。
"""

import argparse
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("エラー: yt-dlp がインストールされていません。", file=sys.stderr)
    print("次のコマンドでインストールしてください:", file=sys.stderr)
    print("    pip3 install yt-dlp", file=sys.stderr)
    sys.exit(1)


def impersonate_target():
    """ブラウザ偽装(impersonation)が利用可能ならChromeのターゲットを返す。

    最近のFacebookはbot対策が強く、偽装なしだと「Cannot parse data」で
    失敗することが多いため、利用可能なら常に有効にする。
    """
    try:
        import curl_cffi  # noqa: F401
        from yt_dlp.networking.impersonate import ImpersonateTarget
        return ImpersonateTarget.from_str("chrome")
    except Exception:
        return None


def build_options(args: argparse.Namespace) -> dict:
    """コマンドライン引数から yt-dlp のオプションを組み立てる。"""
    outdir = Path(args.output).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)

    opts = {
        # MP4優先で最高画質(映像+音声)を取得。だめなら単一ファイルの最良を取得。
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(outdir / "%(title).80s [%(id)s].%(ext)s"),
        "noplaylist": True,
        "retries": 5,
        "concurrent_fragment_downloads": 4,
        # 既に同じ動画をダウンロード済みならスキップ
        "overwrites": False,
    }

    target = impersonate_target()
    if target is not None:
        opts["impersonate"] = target
    else:
        print(
            "注意: ブラウザ偽装(curl_cffi)が利用できません。"
            "Facebookのbot対策で「Cannot parse data」エラーが出る場合は\n"
            '    pipx install "yt-dlp[default,curl-cffi]"\n'
            "でインストールし直してください。",
            file=sys.stderr,
        )

    if args.browser:
        # ブラウザのCookie(ログイン情報)を使う → 非公開動画に対応
        opts["cookiesfrombrowser"] = (args.browser,)
    elif args.cookies:
        # cookies.txt ファイルを使う場合
        opts["cookiefile"] = args.cookies

    if args.audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    if args.list_formats:
        opts["listformats"] = True

    return opts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Facebookの動画をダウンロードするツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "例:\n"
            '  公開動画:        python3 fb_download.py "https://www.facebook.com/watch?v=123456"\n'
            '  非公開動画:      python3 fb_download.py --browser chrome "https://www.facebook.com/..."\n'
            '  音声だけ(MP3):  python3 fb_download.py --audio-only "https://www.facebook.com/..."\n'
        ),
    )
    parser.add_argument("urls", nargs="+", metavar="URL", help="Facebook動画のURL(複数指定可)")
    parser.add_argument(
        "-o", "--output", default="downloads",
        help="保存先フォルダ(デフォルト: downloads)",
    )
    parser.add_argument(
        "--browser", choices=["chrome", "firefox", "edge", "safari", "brave"],
        help="非公開動画用: このブラウザのFacebookログイン情報(Cookie)を使う",
    )
    parser.add_argument(
        "--cookies", metavar="FILE",
        help="非公開動画用: cookies.txt ファイルのパスを指定する",
    )
    parser.add_argument(
        "--audio-only", action="store_true",
        help="動画ではなく音声(MP3)だけを保存する",
    )
    parser.add_argument(
        "--list-formats", action="store_true",
        help="ダウンロードせずに利用可能な画質の一覧だけ表示する",
    )
    args = parser.parse_args()

    opts = build_options(args)

    failed = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        for url in args.urls:
            try:
                print(f"\n=== ダウンロード開始: {url}")
                ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                msg = str(e)
                print(f"\n!!! ダウンロード失敗: {url}", file=sys.stderr)
                if "login" in msg.lower() or "cookies" in msg.lower():
                    print(
                        "ヒント: この動画は非公開の可能性があります。"
                        "--browser chrome のようにログイン中のブラウザを指定してみてください。",
                        file=sys.stderr,
                    )
                elif "cannot parse data" in msg.lower():
                    hints = ["ヒント: 「Cannot parse data」の主な原因と対処:"]
                    if not args.browser and not args.cookies:
                        hints.append(
                            "  1. ログインが必要な動画かもしれません → --browser chrome を付けて再実行"
                        )
                    if impersonate_target() is None:
                        hints.append(
                            "  2. Facebookのbot対策の可能性 → pipx install \"yt-dlp[default,curl-cffi]\" "
                            "で偽装機能付きのyt-dlpを入れて再実行"
                        )
                    print("\n".join(hints), file=sys.stderr)
                failed.append(url)

    if not args.list_formats:
        total = len(args.urls)
        ok = total - len(failed)
        print(f"\n完了: {ok}/{total} 件成功", flush=True)
        if failed:
            print("失敗したURL:", file=sys.stderr)
            for url in failed:
                print(f"  {url}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
