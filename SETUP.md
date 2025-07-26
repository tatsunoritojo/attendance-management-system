# セットアップガイド

## 基本的なセットアップ

### 1. ファイルの準備

1. **フォルダの配置**
   - `attendance-management-system` フォルダを任意の場所に配置
   - 日本語の入ったパスは避けることをお勧めします

2. **生徒データの準備**
   - `assets/sample_data.csv` を編集
   - 実際の生徒ID・名前に書き換えます
   ```csv
   StudentID,StudentName
   2025001,山田太郎
   2025002,鈴木花子
   2025003,田中次郎
   ```

3. **初回起動**
   - `AttendanceManagement.exe` を実行
   - 必要なフォルダが自動で作成されます

### 2. QRコード印刷の設定（必要な場合のみ）

QRコードラベルを印刷したい場合：

1. **Brother P-touch Editorのインストール**
   - Brotherの公式サイトからダウンロード・インストール
   - Brother P-touchシリーズのプリンターが必要です

2. **プリンターの接続**
   - USBまたはWi-Fiでプリンターを接続
   - Windowsでプリンターが認識されることを確認

### 3. Google Drive連携（オプション）

Google Driveと連携する場合：

1. **サービスアカウント作成**
   - Google Cloud Consoleでサービスアカウントを作成
   - JSON認証ファイルをダウンロード

2. **認証ファイル配置**
   - `service_account.json.template` を `service_account.json` にリネーム
   - ダウンロードした認証ファイルの内容で置き換え

3. **スプレッドシート共有**
   - サービスアカウントのメールアドレスにスプレッドシートの編集権限を付与

### 4. 設定のカスタマイズ

`settings.json` で以下の設定を変更可能：

```json
{
  "qr_code_folder": "assets/images/塾生QRコード",
  "output_directory": "output/reports",
  "ptouch_editor_path": "C:\\Program Files (x86)\\Brother\\Ptedit54\\ptedit54.exe",
  "log_level": "INFO"
}
```

## 開発者向けセットアップ

### Python環境での実行

1. **Python環境準備**
   ```bash
   # Python 3.9以降が必要
   python --version
   
   # 仮想環境作成（推奨）
   python -m venv venv
   
   # 仮想環境アクティベート
   # Windows:
   venv\\Scripts\\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **依存関係インストール**
   ```bash
   pip install -r dist-src/requirements.txt
   ```

3. **アプリケーション起動**
   ```bash
   python start_app.py
   ```

### 実行ファイルの再作成

1. **PyInstallerのインストール**
   ```bash
   pip install pyinstaller
   ```

2. **実行ファイル作成**
   ```bash
   # specファイルを使用
   pyinstaller dist-src/attendance_app.spec
   
   # または直接作成
   pyinstaller --onedir --noconsole --add-data "assets;assets" start_app.py
   ```

## トラブルシューティング

### よくある問題

1. **フォントが表示されない**
   - `assets/fonts/UDDigiKyokashoN-R.ttc` が存在することを確認
   - システムフォントの設定を確認

2. **QRコード印刷ができない**
   - Brother P-touch Editorがインストールされているか確認
   - プリンターの接続状態を確認
   - `settings.json` のパス設定を確認

3. **出席データが保存されない**
   - `output/reports` フォルダの書き込み権限を確認
   - ディスク容量を確認

4. **アプリケーションが起動しない**
   - `attendance.log` ファイルでエラー内容を確認
   - 管理者権限で実行を試す

### ログファイルの確認

問題が発生した場合は、アプリケーションフォルダ内の `attendance.log` でエラー詳細を確認できます。

## サポート

技術的な質問や問題報告については、プロジェクトの開発者に連絡してください。