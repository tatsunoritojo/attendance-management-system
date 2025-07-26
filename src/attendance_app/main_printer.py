from pathlib import Path
import sys
import threading
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup

from attendance_app.spreadsheet import get_student_list_for_printing
from attendance_app.print_dialog import PrintDialog
from attendance_app.printer_control import print_label
from attendance_app.print_history import add_record
from attendance_app.font_manager import register_font

# フォント設定を動的に取得
FONT_AVAILABLE, FONT_NAME = register_font()

def show_error_popup(title, message):
    content_label = Label(text=message, font_name=FONT_NAME, font_size="18sp")
    popup = Popup(title=title, content=content_label, size_hint=(0.8, 0.4), title_font=FONT_NAME)
    popup.open()

class PrintScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.is_list_loaded = False
        self.current_student_id = None
        self.current_student_name = None

        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation="vertical", padding=[40, 30, 40, 30], spacing=20)
        header_label = Label(
            text="QRコード印刷システム", 
            font_name=FONT_NAME, 
            font_size="36sp", 
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            size_hint_y=None, 
            height="80dp"
        )
        main_layout.add_widget(header_label)

        # シンプルな縦レイアウトに変更（プレビュー削除）
        content_layout = BoxLayout(orientation="vertical", spacing=20)
        
        # 生徒リスト部分
        list_card = BoxLayout(orientation="vertical", padding=10, spacing=10)
        list_title = Label(text="印刷対象選択", font_name=FONT_NAME, font_size="20sp", size_hint_y=None, height="40dp")
        list_card.add_widget(list_title)

        self.qr_list_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.qr_list_layout.bind(minimum_height=self.qr_list_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 0.7))  # スクロールビューの高さを調整
        scroll_view.add_widget(self.qr_list_layout)
        list_card.add_widget(scroll_view)

        # 選択した生徒の表示エリア
        self.selected_label = Label(
            text="選択された生徒: なし",
            font_name=FONT_NAME,
            font_size="18sp",
            size_hint_y=None,
            height="50dp"
        )
        list_card.add_widget(self.selected_label)

        content_layout.add_widget(list_card)

        # ボタンエリア
        buttons_layout = BoxLayout(size_hint_y=None, height="80dp", spacing=20)
        
        update_btn = Button(
            text="リスト更新", 
            font_name=FONT_NAME, 
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        update_btn.bind(on_release=self.update_list)
        buttons_layout.add_widget(update_btn)

        print_button = Button(
            text="印刷実行", 
            font_name=FONT_NAME, 
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        print_button.bind(on_release=self.confirm_print)
        buttons_layout.add_widget(print_button)

        back_btn = Button(
            text="戻る", 
            font_name=FONT_NAME, 
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "wait"))
        buttons_layout.add_widget(back_btn)
        
        content_layout.add_widget(buttons_layout)
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)
        
        self._show_initial_message()

    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _show_initial_message(self):
        self.qr_list_layout.clear_widgets()
        initial_message = Label(text="「リスト更新」をクリックしてください", font_name=FONT_NAME, font_size="18sp")
        self.qr_list_layout.add_widget(initial_message)

    def update_list(self, *args):
        """リスト更新ボタンが押された時の処理"""
        self.qr_list_layout.clear_widgets()
        loading_label = Label(text="リストを読み込み中...", font_name=FONT_NAME, font_size="18sp")
        self.qr_list_layout.add_widget(loading_label)
        threading.Thread(target=self._load_printable_list_thread).start()

    def _load_printable_list_thread(self):
        """別スレッドで生徒リストを読み込み"""
        try:
            student_list = get_student_list_for_printing()
            Clock.schedule_once(lambda dt: self._update_qr_list_ui(student_list), 0)
            self.is_list_loaded = True
        except Exception as e:
            Clock.schedule_once(lambda dt: show_error_popup("エラー", f"リストの読み込みに失敗: {e}"), 0)

    def _update_qr_list_ui(self, printable_students):
        """UIに生徒リストを表示"""
        self.qr_list_layout.clear_widgets()
        
        if not printable_students:
            empty_message = Label(text="印刷可能な生徒が見つかりません", font_name=FONT_NAME, font_size="16sp")
            self.qr_list_layout.add_widget(empty_message)
            return

        for student_data in printable_students:
            display_text = f"{student_data['id']} - {student_data['name']}"
            btn = Button(text=display_text, size_hint_y=None, height="55dp", font_name=FONT_NAME, font_size="16sp")
            btn.bind(on_release=lambda _, data=student_data: self.select_student(data))
            self.qr_list_layout.add_widget(btn)

    def select_student(self, student_data):
        """生徒を選択した時の処理（プレビュー機能削除）"""
        self.current_student_id = student_data['id']
        self.current_student_name = student_data['name']
        
        # 選択した生徒を表示
        self.selected_label.text = f"選択された生徒: {self.current_student_name} ({self.current_student_id})"

    def confirm_print(self, *args):
        """印刷実行ボタンが押された時の処理"""
        if not self.current_student_id or not self.current_student_name:
            show_error_popup("選択エラー", "印刷する生徒をリストから選択してください。")
            return

        student_id = self.current_student_id
        student_name = self.current_student_name

        def on_confirm():
            threading.Thread(target=self._print_qr_thread, args=(student_id, student_name)).start()

        dialog = PrintDialog(f"{student_name} のQRコード", on_confirm, lambda: None)
        dialog.open()

    def _print_qr_thread(self, student_id, student_name):
        """別スレッドで印刷処理を実行"""
        try:
            print_label(student_id, student_name)
            add_record(student_id, student_name, 'success')
            Clock.schedule_once(lambda dt: show_error_popup("成功", f"{student_name} のQRコードを印刷しました"), 0)
        except Exception as e:
            add_record(student_id, student_name, 'failure', str(e))
            Clock.schedule_once(lambda dt, error_msg=str(e): show_error_popup("エラー", f"印刷に失敗しました: {error_msg}"), 0)