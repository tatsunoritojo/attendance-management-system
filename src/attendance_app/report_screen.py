import os
import threading
from datetime import datetime
from pathlib import Path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.text import LabelBase

from attendance_app.report_system.excel_report_generator import generate_excel_reports
from attendance_app.report_system.utils import get_current_month_year, list_generated_reports
from attendance_app.spreadsheet import sync_attendance_to_excel # 追加

# フォント設定を動的に取得（font_manager.pyの関数を利用）
try:
    from attendance_app.font_manager import register_font
    FONT_AVAILABLE, FONT_NAME = register_font()
except ImportError:
    # フォールバック
    FONT_AVAILABLE, FONT_NAME = False, "Roboto"

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        self.create_ui()

    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def create_ui(self):
        main_layout = BoxLayout(orientation="vertical", spacing=20, padding=[40, 30, 40, 30])
        title_label = Label(
            text="月次Excelレポート生成", 
            font_name=FONT_NAME, 
            font_size="36sp", 
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            size_hint_y=None, 
            height="80dp"
        )
        main_layout.add_widget(title_label)

        date_section = self.create_date_selection_section()
        main_layout.add_widget(date_section)

        options_section = self.create_options_section()
        main_layout.add_widget(options_section)

        # Excel同期ボタンを追加
        sync_button = Button(
            text="出席情報をExcelに同期", 
            font_name=FONT_NAME, 
            size_hint_y=None, 
            height="50dp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        sync_button.bind(on_press=self.sync_to_excel)
        main_layout.add_widget(sync_button)

        self.progress_label = Label(text="", font_name=FONT_NAME, size_hint_y=None, height="30dp")
        main_layout.add_widget(self.progress_label)

        reports_section = self.create_reports_list_section()
        main_layout.add_widget(reports_section)

        back_button = Button(
            text="メインメニューに戻る", 
            font_name=FONT_NAME, 
            size_hint_y=None, 
            height="50dp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        back_button.bind(on_press=lambda *_: setattr(self.manager, "current", "wait"))
        main_layout.add_widget(back_button)
        self.add_widget(main_layout)

    def create_date_selection_section(self):
        section = BoxLayout(orientation="horizontal", size_hint_y=None, height="60dp", spacing=10)
        current_year, current_month = get_current_month_year()
        section.add_widget(Label(text="対象年月:", font_name=FONT_NAME, size_hint_x=None, width="100dp"))
        self.year_spinner = Spinner(text=str(current_year), values=[str(y) for y in range(2020, 2030)], size_hint_x=None, width="100dp")
        section.add_widget(self.year_spinner)
        section.add_widget(Label(text="年", font_name=FONT_NAME, size_hint_x=None, width="30dp"))
        self.month_spinner = Spinner(text=str(current_month), values=[str(m) for m in range(1, 13)], size_hint_x=None, width="80dp")
        section.add_widget(self.month_spinner)
        section.add_widget(Label(text="月", font_name=FONT_NAME, size_hint_x=None, width="30dp"))
        return section

    def create_options_section(self):
        section = BoxLayout(size_hint_y=None, height="60dp", spacing=10)
        excel_button = Button(text="Excelレポート一括生成", font_name=FONT_NAME)
        excel_button.bind(on_press=self.generate_excel_report)
        section.add_widget(excel_button)
        open_folder_button = Button(text="レポートフォルダを開く", font_name=FONT_NAME)
        open_folder_button.bind(on_press=self.open_reports_folder)
        section.add_widget(open_folder_button)
        return section

    def create_reports_list_section(self):
        section = BoxLayout(orientation="vertical", spacing=10)
        section.add_widget(Label(text="生成されたレポート", font_name=FONT_NAME, size_hint_y=None, height="30dp"))
        refresh_button = Button(text="リストを更新", font_name=FONT_NAME, size_hint_y=None, height="40dp")
        refresh_button.bind(on_press=self.refresh_reports_list)
        section.add_widget(refresh_button)
        self.reports_list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5)
        self.reports_list_layout.bind(minimum_height=self.reports_list_layout.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.reports_list_layout)
        section.add_widget(scroll)
        self.refresh_reports_list()
        return section

    def refresh_reports_list(self, instance=None):
        self.reports_list_layout.clear_widgets()
        reports = list_generated_reports()
        if not reports:
            self.reports_list_layout.add_widget(Label(text="生成されたレポートはありません", font_name=FONT_NAME, size_hint_y=None, height="40dp", color=(0.1, 0.1, 0.1, 1)))
        else:
            for report in reports:
                if not report['name'].endswith('.xlsx'): continue
                item = BoxLayout(size_hint_y=None, height="40dp", spacing=10)
                item.add_widget(Label(text=report['name'], font_name=FONT_NAME, size_hint_x=0.7, color=(0.1, 0.1, 0.1, 1)))
                open_btn = Button(text="開く", font_name=FONT_NAME, size_hint_x=0.3)
                open_btn.bind(on_press=lambda x, path=report['full_path']: self.open_report(path))
                item.add_widget(open_btn)
                self.reports_list_layout.add_widget(item)

    def generate_excel_report(self, instance):
        year = int(self.year_spinner.text)
        month = int(self.month_spinner.text)
        self.progress_label.text = f"{year}年{month}月のExcelレポートを生成中..."
        threading.Thread(target=self._generate_excel_thread, args=(year, month), daemon=True).start()

    def _generate_excel_thread(self, year, month):
        try:
            file_path = generate_excel_reports(year, month)
            if file_path:
                message = f"Excelレポートが生成されました。\n{os.path.basename(file_path)}"
                Clock.schedule_once(lambda dt: self.on_generation_complete(message))
            else:
                Clock.schedule_once(lambda dt: self.on_generation_error("レポートファイルが生成されませんでした"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_generation_error(str(e)))

    def sync_to_excel(self, instance):
        self.progress_label.text = "出席情報をExcelに同期中..."
        threading.Thread(target=self._sync_to_excel_thread, daemon=True).start()

    def _sync_to_excel_thread(self):
        try:
            success = sync_attendance_to_excel()
            if success:
                message = "出席情報がExcelに同期されました。"
            else:
                message = "出席情報のExcel同期に失敗しました。ログを確認してください。"
            Clock.schedule_once(lambda dt: self.on_sync_complete(message))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_sync_error(str(e)))

    def open_reports_folder(self, instance):
        try:
            from attendance_app.path_manager import get_output_dir
            reports_dir = get_output_dir()
            os.startfile(str(reports_dir))
        except Exception as e:
            self.show_popup("エラー", f"フォルダを開けませんでした: {e}")

    def open_report(self, file_path):
        try:
            os.startfile(file_path)
        except Exception as e:
            self.show_popup("エラー", f"ファイルを開けませんでした: {e}")

    def on_generation_complete(self, message):
        self.progress_label.text = ""
        self.refresh_reports_list()
        self.show_popup("完了", message)

    def on_generation_error(self, error_message):
        self.progress_label.text = ""
        self.show_popup("エラー", f"レポート生成中にエラーが発生しました: {error_message}")

    def on_sync_complete(self, message):
        self.progress_label.text = ""
        self.show_popup("完了", message)

    def on_sync_error(self, error_message):
        self.progress_label.text = ""
        self.show_popup("エラー", f"Excel同期中にエラーが発生しました: {error_message}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message, font_name=FONT_NAME), size_hint=(0.8, 0.4))
        popup.open()

