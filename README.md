# 出席管理システム - Python業務自動化の実装事例

## 概要

Excelでの手作業によるデータ管理をPythonで自動化した出席管理システムです。教育現場でよくある「生徒の入退室管理」を題材に、QRコードを使った効率的な出席記録システムを開発しました。

外部サービスに依存せず、ローカルのCSVファイルでデータを管理することで、導入コストを抑えつつ、実用的な業務改善を実現しています。

## 主な機能

- **QRコード出席記録**: 生徒がQRコードをかざすだけで入退室時刻を自動記録
- **シンプルなデータ管理**: 生徒情報はCSVファイル（`assets/sample_data.csv`）で管理
- **QRコードラベル印刷**: Brother P-touch Editorと連携して、生徒用のQRコードラベルを印刷
- **出席レポート作成**: 月ごとの出席状況をPDFやExcel形式で出力

## ファイル構成

```
attendance-management-system/
├── AttendanceManagement.exe     # メインアプリケーション（PyInstallerで作成）
├── README.md                    # このファイル
├── settings.json               # 設定ファイル
├── service_account.json.template # Google認証テンプレート（必要に応じて）
├── start_app.py                # 開発用起動スクリプト
├── assets/                     # アセットファイル
│   ├── fonts/                  # フォントファイル
│   ├── images/                 # 画像ファイル
│   ├── sounds/                 # 音声ファイル
│   ├── sample_data.csv         # 生徒データ（要編集）
│   └── Sample_Data.xlsx        # Excelファイル形式の生徒データ
├── output/                     # 出力フォルダ
│   └── reports/               # レポート保存先
├── docs/                      # ドキュメント
└── dist-src/                  # 配布用ソースコード
    ├── requirements.txt
    ├── attendance_app.spec    # PyInstaller設定
    └── src/                   # Pythonソースコード
```

## 使い方

### すぐに試したい場合

1. **生徒データを準備**
   - `assets/sample_data.csv` を開いて編集
   - 実際の生徒ID・名前に変更
   ```csv
   StudentID,StudentName
   2025001,山田太郎
   2025002,鈴木花子
   ```

2. **アプリを起動**
   - `AttendanceManagement.exe` をダブルクリック

### 開発者の方へ

1. **Python環境の準備**
   ```bash
   pip install -r dist-src/requirements.txt
   ```

2. **ソースコードから実行**
   ```bash
   python start_app.py
   ```

## 操作の流れ

1. **出席記録**: QRコードをスキャンするか、生徒IDを手入力して入退室を記録
2. **ラベル印刷**: 印刷画面で生徒を選んでQRコードラベルを作成
3. **レポート確認**: 月を指定して出席状況をPDFやExcelで出力

## 動作環境

- **OS**: Windows 10/11
- **プリンター**: Brother P-touch Editor（QRコード印刷する場合）
- **開発用**: Python 3.9以降

## トラブル時は

問題が発生した場合は、`docs/` フォルダ内の詳しい説明を参考にしてください。

## 使用している技術

このシステムでは以下のPython技術を組み合わせて作っています：

- **GUI**: Kivyを使ったデスクトップアプリ
- **データ処理**: CSV/Excelファイルの読み書きにopenpyxlを使用
- **PDF作成**: ReportLabでレポートを生成
- **QRコード・印刷**: 画像処理とプリンター制御
- **設定管理**: JSONファイルと環境変数で設定を管理
- **実行ファイル化**: PyInstallerでexeファイルを作成

## 作成の背景

このプロジェクトは、実際の教育現場でExcelを使った手作業の出席管理を改善するために作成しました。同じような業務でお困りの方に、Python自動化の参考事例として活用していただければと思います。