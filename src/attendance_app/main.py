# attendance_app.py

"""
Attendance Management System v3.4 Main Application
Cross-platform support with improved configuration management.
"""

import threading
import sys
import logging
import os
from datetime import datetime
from pathlib import Path
from attendance_app.settings import settings_manager
from attendance_app.path_manager import get_font_path, get_image_path, get_sound_path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from attendance_app.config import load_settings, save_settings, validate_configuration
from attendance_app.spreadsheet import get_student_name, get_last_record, write_exit, append_entry, write_response
from attendance_app.main_printer import PrintScreen
from attendance_app.report_screen import ReportScreen
from attendance_app.student_registry_screen import StudentRegistryScreen

logger = logging.getLogger(__name__)

# 音声ファイルをロード（アプリ起動時に1回だけ）
def load_select_sound():
    """選択音声をロードする"""
    try:
        sound_path = str(get_sound_path("selecte_sound.mp3"))
        if os.path.exists(sound_path):
            sound = SoundLoader.load(sound_path)
            if sound:
                logger.info(f"Select sound loaded: {sound_path}")
                return sound
            else:
                logger.warning(f"Failed to load sound: {sound_path}")
        else:
            logger.warning(f"Sound file not found: {sound_path}")
    except Exception as e:
        logger.error(f"Error loading select sound: {e}")
    return None

# グローバルな音声オブジェクト
SELECT_SOUND = load_select_sound()

def play_select_sound():
    """選択音声を再生する"""
    try:
        if SELECT_SOUND:
            SELECT_SOUND.play()
            logger.info("Select sound played")
        else:
            logger.warning("Select sound not available")
    except Exception as e:
        logger.error(f"Error playing select sound: {e}")

# フォント管理機能は font_manager.py に移動されました
from attendance_app.font_manager import register_font

# フォント登録実行
FONT_AVAILABLE, FONT_NAME = register_font()

    # --- エラーハンドリング付きユーティリティ関数 ---
def show_error_popup(title, message):
    """エラーメッセージを表示するポップアップ - 改善されたデザイン"""
    from kivy.graphics import Color, Rectangle
    
    # カスタムコンテンツレイアウト
    content_layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
    
    # メッセージラベル
    content_label = Label(
        text=message,
        font_name=FONT_NAME,
        font_size="18sp",
        color=(0.2, 0.2, 0.2, 1),
        halign="center",
        valign="middle"
    )
    content_label.text_size = (None, None)
    content_layout.add_widget(content_label)
    
    # 閉じるボタン
    close_btn = Button(
        text="確認",
        size_hint_y=None,
        height="50dp",
        font_name=FONT_NAME,
        font_size="16sp",
        background_color=(0.4, 0.7, 0.8, 1),  # 柔らかい水色
        color=(1, 1, 1, 1),  # 白文字
        background_normal=''
    )
    content_layout.add_widget(close_btn)
    
    popup = Popup(
        title=title,
        content=content_layout,
        size_hint=(0.8, 0.5),
        title_font=FONT_NAME,
        auto_dismiss=False
    )
    
    # 背景色設定
    with popup.canvas.before:
        Color(0.98, 0.98, 0.98, 1)  # 薄いグレー背景
        popup.bg_rect = Rectangle(size=popup.size, pos=popup.pos)
    popup.bind(size=lambda instance, value: setattr(popup.bg_rect, 'size', value))
    popup.bind(pos=lambda instance, value: setattr(popup.bg_rect, 'pos', value))
    
    close_btn.bind(on_release=popup.dismiss)
    popup.open()

class HelpPopup(Popup):
    def __init__(self, title, message, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = "UDDigiKyokashoN-R" if FONT_AVAILABLE else "Roboto"
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False

        # テキストコンテンツの左右パディング
        self.text_horizontal_padding = 40  # ここでパディングを調整できます

        self.content_label = Label(
            text=message,
            font_name=FONT_NAME,
            font_size="18sp",
            size_hint_y=None,
            valign="top",
            halign="left",
            text_size=(600, None)  # 適切な幅を設定
        )
        self.content_label.bind(texture_size=self.content_label.setter('size'))

        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.content_label)

        close_button = Button(
            text="閉じる",
            size_hint=(1, 0.1),
            font_name=FONT_NAME,
        )
        close_button.bind(on_release=self.dismiss)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(scroll_view)
        layout.add_widget(close_button)
        self.content = layout

    def on_size(self, instance, value):
        # ポップアップのサイズ変更時にテキストの幅を更新
        if self.content_label:
            # content (BoxLayout) の幅から明示的なパディングを引く
            content_width = max(400, self.content.width - self.text_horizontal_padding)
            self.content_label.text_size = (content_width, None)


# --- 各画面定義 ---
class WaitScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        # 背景色設定（薄いグレー）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.96, 0.96, 1)  # 薄いグレー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        root = BoxLayout(orientation="vertical")
        from kivy.uix.widget import Widget
        
        # ヘッダー改善 - より洗練されたデザイン
        header = BoxLayout(size_hint_y=None, height="60dp", padding=[20, 10, 20, 10])
        header.add_widget(Widget())
        
        # 設定ボタン - エレガントブルー系
        settings_btn = Button(
            text="設定", 
            size_hint=(None, 1), 
            width=120, 
            font_name=FONT_NAME,
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        settings_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "settings"))
        header.add_widget(settings_btn)
        
        # スペーサー
        header.add_widget(Widget(size_hint_x=None, width=10))
        
        # 印刷ボタン - エレガントブルー系
        print_btn = Button(
            text="印刷", 
            size_hint=(None, 1), 
            width=120, 
            font_name=FONT_NAME,
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        print_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "print_screen"))
        header.add_widget(print_btn)
        
        # スペーサー
        header.add_widget(Widget(size_hint_x=None, width=10))
        
        # レポート生成ボタン - エレガントブルー系
        report_btn = Button(
            text="レポート", 
            size_hint=(None, 1), 
            width=120, 
            font_name=FONT_NAME,
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        report_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "report"))
        header.add_widget(report_btn)
        
        # スペーサー
        header.add_widget(Widget(size_hint_x=None, width=10))
        
        # 名簿管理ボタン - エレガントブルー系
        registry_btn = Button(
            text="名簿管理", 
            size_hint=(None, 1), 
            width=120, 
            font_name=FONT_NAME,
            font_size="18sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        registry_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "student_registry"))
        header.add_widget(registry_btn)
        
        root.add_widget(header)

        # メインコンテンツエリア - 洗練されたセンタリングレイアウト
        layout = BoxLayout(orientation="vertical", padding=[80, 40, 80, 40], spacing=40)
        
        # 上部スペーサー
        layout.add_widget(Widget(size_hint_y=0.3))
        
        # メインタイトル - 大型でインパクトのある表示
        title_label = Label(
            text="学生番号を入力",
            font_name=FONT_NAME,
            font_size="48sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー
            size_hint_y=None,
            height="100dp",
            bold=True
        )
        layout.add_widget(title_label)
        
        # サブタイトル - エレガントな説明文
        instruction_label = Label(
            text="生徒証をスキャンまたは直接入力してください",
            font_name=FONT_NAME,
            font_size="24sp",
            color=(0.4, 0.4, 0.4, 1),  # ミディアムグレー
            size_hint_y=None,
            height="40dp",
            halign="center"
        )
        instruction_label.text_size = (instruction_label.width, None)
        instruction_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        layout.add_widget(instruction_label)
        
        # 中間スペーサー
        layout.add_widget(Widget(size_hint_y=0.2))
        
        # 入力フィールドコンテナ - ミニマルで洗練されたデザイン
        input_container = BoxLayout(orientation="vertical", spacing=25)
        
        # メイン入力フィールド - 大型で視認性の高いデザイン
        try:
            self.input = TextInput(
                hint_text="学生番号を入力してください",
                multiline=False,
                font_name=FONT_NAME if FONT_AVAILABLE else "Roboto",
                font_size="36sp",
                size_hint=(1, None),
                height="140dp",
                background_color=(1, 1, 1, 1),  # 純白背景
                foreground_color=(0.1, 0.1, 0.1, 1),  # 濃いグレー文字
                cursor_color=(0.3, 0.6, 0.9, 1),  # エレガントなブルー
                selection_color=(0.3, 0.6, 0.9, 0.2),  # 薄いブルー選択
                padding=[30, 30],
                write_tab=False,
                halign="center"
            )
            # イベントバインド
            self.input.bind(on_text_validate=self.safe_on_submit)
            self.input.bind(focus=self._on_focus_change)
            self.input.bind(text=self._on_text_change)
            logger.info("TextInput created successfully")
        except Exception as e:
            logger.error(f"Error creating TextInput: {e}")
            # フォールバック
            self.input = TextInput(
                hint_text="学生番号を入力",
                multiline=False,
                font_size="36sp",
                size_hint=(1, None),
                height="140dp"
            )
            self.input.bind(on_text_validate=self.safe_on_submit)
        
        input_container.add_widget(self.input)
        
        # エレガントな送信ボタン
        btn = Button(
            text="→ 送信",
            font_name=FONT_NAME,
            font_size="28sp",
            size_hint=(1, None),
            height="90dp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントなブルー
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        btn.bind(on_press=self.safe_on_submit)
        input_container.add_widget(btn)
        
        layout.add_widget(input_container)
        
        # 下部スペーサー
        layout.add_widget(Widget(size_hint_y=0.5))
        
        root.add_widget(layout)
        self.add_widget(root)
        
    def on_enter(self):
        """画面に入った時の処理 - 自動フォーカス設定"""
        try:
            if hasattr(self, 'input') and self.input:
                # 少し遅延させてからフォーカス（UIの準備完了を待つ）
                Clock.schedule_once(self._focus_input, 0.1)
                logger.info("Scheduled auto-focus for input field")
        except Exception as e:
            logger.error(f"Error in on_enter: {e}")
            
    def _focus_input(self, dt):
        """入力フィールドにフォーカスを設定"""
        try:
            if hasattr(self, 'input') and self.input:
                self.input.focus = True
                logger.info("Auto-focus applied to input field")
        except Exception as e:
            logger.error(f"Error setting focus: {e}")
    
    def _on_focus_change(self, instance, value):
        """フォーカス変更時の視覚的フィードバック"""
        try:
            if value:  # フォーカスされた時
                # エレガントなブルー系のフォーカス効果
                instance.background_color = (0.97, 0.99, 1, 1)
                logger.info("Input field focused - visual feedback applied")
                # Wait画面では音声なし（質問画面でのみ音声再生）
            else:  # フォーカスが外れた時
                instance.background_color = (1, 1, 1, 1)
                logger.info("Input field unfocused")
        except Exception as e:
            logger.error(f"Error in focus change handler: {e}")
    
    def _on_text_change(self, instance, value):
        """テキスト変更時のフィードバック"""
        try:
            if value:  # テキストが入力された時
                # 入力があることを示すエレガントな色変更
                instance.background_color = (0.95, 0.98, 1, 1)
                logger.info(f"Text input detected: {len(value)} characters")
            else:  # テキストが空の時
                if instance.focus:
                    instance.background_color = (0.97, 0.99, 1, 1)
                else:
                    instance.background_color = (1, 1, 1, 1)
        except Exception as e:
            logger.error(f"Error in text change handler: {e}")
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def safe_on_submit(self, *_):
        """安全なテキスト入力処理 - エラーハンドリング強化版"""
        try:
            if not hasattr(self, 'input') or not self.input:
                logger.error("TextInput not available")
                return
                
            sid = self.input.text.strip()
            logger.info(f"Student ID entered: {sid}")
            
            if not sid:
                logger.info("Student ID is empty, returning.")
                return

            # 入力フィールドをすぐにクリア
            self.input.text = ""
            
            app = App.get_running_app()
            if not app:
                logger.error("App instance not available")
                return
                
            app.student_id = sid
            
            # UI更新を安全に実行
            try:
                self.manager.current = "loading"
            except Exception as e:
                logger.error(f"Failed to switch to loading screen: {e}")
                return

            # 処理を別スレッドで実行
            try:
                thread = threading.Thread(
                    target=self._safe_process_student_id, 
                    args=(sid,),
                    daemon=True
                )
                thread.start()
                logger.info(f"Started processing thread for student ID: {sid}")
            except Exception as e:
                logger.error(f"Failed to start processing thread: {e}")
                Clock.schedule_once(lambda dt: show_error_popup("エラー", f"処理の開始に失敗しました: {e}"), 0)
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                
        except Exception as e:
            logger.error(f"Error in safe_on_submit: {e}")
            try:
                Clock.schedule_once(lambda dt: show_error_popup("エラー", f"入力処理でエラーが発生しました: {e}"), 0)
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
            except Exception as e2:
                logger.error(f"Failed to show error popup: {e2}")

    def on_submit(self, *_):
        """後方互換性のため残存 - safe_on_submitにリダイレクト"""
        self.safe_on_submit(*_)

    def _safe_process_student_id(self, sid):
        """安全な生徒ID処理 - 詳細なエラーハンドリング付き"""
        try:
            logger.info(f"Starting student ID processing for: {sid}")
            
            app = App.get_running_app()
            if not app:
                logger.error("App instance not available in processing thread")
                Clock.schedule_once(lambda dt: show_error_popup("エラー", "アプリケーションインスタンスが利用できません"), 0)
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                return

            # Step 1: 生徒名を取得
            try:
                logger.info(f"Getting student name for ID: {sid}")
                name = get_student_name(sid)
                logger.info(f"Student name result: {repr(name)}")
                
                if name == "Unknown":
                    logger.info(f"Student ID {sid} not found")
                    Clock.schedule_once(lambda dt: show_error_popup("エラー", f"生徒ID「{sid}」が見つかりません。\n正しいIDを入力してください。"), 0)
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                    return
            except Exception as e:
                logger.error(f"Error getting student name: {e}")
                Clock.schedule_once(lambda dt: show_error_popup("エラー", f"生徒情報の取得に失敗しました: {e}"), 0)
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                return

            # Step 2: 最後の記録を取得
            try:
                logger.info(f"Getting last record for ID: {sid}")
                last_row, last_exit = get_last_record(sid)
                logger.info(f"Last record result: row={last_row}, exit={repr(last_exit)}")
            except Exception as e:
                logger.error(f"Error getting last record: {e}")
                Clock.schedule_once(lambda dt: show_error_popup("エラー", f"出席記録の取得に失敗しました: {e}"), 0)
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                return

            # Step 3: 入室/退室処理
            if last_row and not last_exit:
                # 退室処理
                logger.info(f"Processing exit for student: {sid}")
                try:
                    if write_exit(last_row):
                        app.student_name = name
                        logger.info(f"Exit successful for student: {sid}")
                        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "goodbye"), 0)
                    else:
                        logger.error(f"Exit processing failed for student: {sid}")
                        Clock.schedule_once(lambda dt: show_error_popup("エラー", "退出処理に失敗しました"), 0)
                        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                except Exception as e:
                    logger.error(f"Error in exit processing: {e}")
                    Clock.schedule_once(lambda dt: show_error_popup("エラー", f"退出処理でエラーが発生しました: {e}"), 0)
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
            else:
                # 入室処理
                logger.info(f"Processing entry for student: {sid}")
                try:
                    row_idx = append_entry(sid, name)
                    if row_idx is not None:
                        app.current_record_row = row_idx
                        app.student_name = name
                        logger.info(f"Entry successful for student: {sid}, row: {row_idx}")
                        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "greeting"), 0)
                    else:
                        logger.error(f"Entry processing failed for student: {sid}")
                        Clock.schedule_once(lambda dt: show_error_popup("エラー", "入室処理に失敗しました"), 0)
                        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                except Exception as e:
                    logger.error(f"Error in entry processing: {e}")
                    Clock.schedule_once(lambda dt: show_error_popup("エラー", f"入室処理でエラーが発生しました: {e}"), 0)
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)
                    
            logger.info(f"Student ID processing completed for: {sid}")
            
        except Exception as e:
            logger.error(f"Unexpected error in student ID processing: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            Clock.schedule_once(lambda dt: show_error_popup("エラー", f"処理中に予期しないエラーが発生しました: {e}"), 0)
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 0)

    def _process_student_id(self, sid):
        """後方互換性のため残存 - _safe_process_student_idにリダイレクト"""
        self._safe_process_student_id(sid)


class GreetingScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation="vertical", padding=[80, 60, 80, 60], spacing=40)
        
        # 挨拶ラベル - エレガントなデザイン
        greeting_label = Label(
            text=f"こんにちは！\n{App.get_running_app().student_name} さん",
            font_name=FONT_NAME,
            font_size="42sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            halign="center",
            valign="middle"
        )
        greeting_label.text_size = (None, None)
        layout.add_widget(greeting_label)
        
        # 2秒後に質問画面へ
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "q1"), 2)
        self.add_widget(layout)
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class WeatherToggle(ToggleButton):
    value = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 選択時のエフェクト用
        self.original_background = self.background_normal
        
    def on_state(self, widget, value):
        """選択状態に応じて視覚効果を変更"""
        if value == 'down':
            # 選択時: 明るくする
            self.background_color = (1.2, 1.2, 1.2, 1)
        else:
            # 非選択時: 元に戻す
            self.background_color = (1, 1, 1, 1)


class QuestionScreen(Screen):
    def __init__(self, key, question, next_screen, question_type="weather", **kw):
        super().__init__(**kw)
        self.key = key
        self.next_screen = next_screen
        self.question_type = question_type

        # 背景をエレガントなブルーテーマに設定
        from kivy.graphics import Color, Rectangle

        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation="vertical", padding=[60, 40, 60, 40], spacing=40)

        # 上部スペーサー
        from kivy.uix.widget import Widget
        layout.add_widget(Widget(size_hint_y=0.2))

        # 質問文 - 洗練されたタイポグラフィー
        question_label = Label(
            text=question,
            font_name=FONT_NAME,
            font_size="36sp",
            size_hint_y=None,
            height="100dp",
            valign="middle",
            halign="center",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー
        )
        question_label.text_size = (None, None)
        layout.add_widget(question_label)

        # スペーサーを追加
        from kivy.uix.widget import Widget

        layout.add_widget(Widget(size_hint_y=0.3))

        # 質問タイプに応じて選択肢を作成
        if question_type == "weather":
            self._create_weather_options(layout)
        elif question_type == "sleep":
            self._create_sleep_options(layout)
        elif question_type == "purpose":
            self._create_purpose_options(layout)

        # 下部スペーサー
        layout.add_widget(Widget(size_hint_y=0.3))

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _create_weather_options(self, layout):
        """天気アイコンの選択肢を作成"""
        icon_bar = BoxLayout(
            orientation="horizontal",
            spacing=20,
            size_hint_y=None,
            height="260dp",  # 正方形の天気アイコンに合わせて調整
        )

        weather_options = [
            ("sun.png", "快晴"),
            ("sun_cloud.png", "晴れ"),
            ("cloud.png", "くもり"),
            ("rain.png", "雨"),
            ("heavyrain.png", "豪雨"),
        ]

        for filename, value in weather_options:
            image_path = str(get_image_path(f"weather/{filename}"))
            if os.path.exists(image_path):
                btn = WeatherToggle(
                    background_normal=image_path,
                    background_down=image_path,
                    size_hint=(0.2, 1),  # 全て同じサイズに統一
                    value=value,
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                )
            else:
                # 画像がない場合は通常のボタンを使用
                btn = ToggleButton(
                    text=value,
                    font_name=FONT_NAME,
                    font_size="16sp",
                    size_hint=(0.2, 1),  # 全て同じサイズに統一
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                )

            btn.bind(on_press=lambda button, val=value: self.on_answer(val))
            icon_bar.add_widget(btn)

        layout.add_widget(icon_bar)

    def _create_sleep_options(self, layout):
        """睡眠満足度のビーカーアイコン選択肢を作成"""
        icon_bar = BoxLayout(
            orientation="horizontal",
            spacing=20,
            size_hint_y=None,
            height="350dp",  # 縦長のビーカーに合わせて高さを大きく
        )

        sleep_options = [
            ("beaker1.png", "100％"),
            ("beaker2.png", "75％"),
            ("beaker3.png", "50％"),
            ("beaker4.png", "25％"),
            ("beaker5.png", "0％"),
        ]

        for filename, value in sleep_options:
            image_path = str(get_image_path(f"sleep/{filename}"))
            if os.path.exists(image_path):
                btn = WeatherToggle(
                    background_normal=image_path,
                    background_down=image_path,
                    size_hint=(1, 1),
                    size_hint_min_x=130,  # 縦長に合わせて幅を調整
                    value=value,
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                )
            else:
                # 画像がない場合は通常のボタンを使用
                btn = ToggleButton(
                    text=value,
                    font_name=FONT_NAME,
                    font_size="20sp",
                    size_hint=(1, 1),
                    size_hint_min_x=130,
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                )

            btn.bind(on_press=lambda button, val=value: self.on_answer(val))
            icon_bar.add_widget(btn)

        layout.add_widget(icon_bar)

    def _create_purpose_options(self, layout):
        """目的の文字ボタン選択肢を作成"""
        # 画像挿入枠を追加（中段）
        icon_bar = BoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height="300dp")

        purpose_images = [
            ("purpose1.png", "来る"),
            ("purpose2.png", "学ぶ"),
            ("purpose3.png", "話す"),
            ("purpose4.png", "楽しむ"),
            ("purpose5.png", "整える"),
        ]

        for filename, value in purpose_images:
            image_path = str(get_image_path(f"purpose/{filename}"))
            if os.path.exists(image_path):
                btn = WeatherToggle(
                    background_normal=image_path,
                    background_down=image_path,
                    size_hint=(1, 1),
                    size_hint_min_x=120,
                    value=value,
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                )
                btn.bind(on_press=lambda button, val=value: self.on_answer(val))
            else:
                # 画像がない場合は空のプレースホルダーを使用
                btn = ToggleButton(
                    text="画像なし",
                    font_name=FONT_NAME,
                    font_size="16sp",
                    size_hint=(1, 1),
                    size_hint_min_x=120,
                    group=f"question_{self.key}",
                    allow_no_selection=False,
                    background_color=(0.9, 0.9, 0.9, 1),  # 薄いグレーで表示
                )
                btn.bind(on_press=lambda button, val=value: self.on_answer(val))

            icon_bar.add_widget(btn)

        layout.add_widget(icon_bar)

        # スペーサーを追加してボタンを下に移動
        from kivy.uix.widget import Widget

        layout.add_widget(Widget(size_hint_y=0.2))

        # ボタンレイアウト（下段）
        button_layout = BoxLayout(
            orientation="horizontal", spacing=20, size_hint_y=None, height="80dp", size_hint_x=1
        )

        purpose_options = ["来る", "学ぶ", "話す", "楽しむ", "整える"]

        for purpose in purpose_options:
            btn = Button(
                text=purpose,
                font_name=FONT_NAME,
                font_size="24sp",  # 文字サイズを大きく
                size_hint=(1, 1),  # 均等に配置
                size_hint_min_x=140,  # 最小幅を確保
            )
            btn.bind(on_press=lambda button, val=purpose: self.on_answer(val))
            button_layout.add_widget(btn)

        layout.add_widget(button_layout)

    def on_answer(self, value):
        """回答処理"""
        # 選択音声を再生
        play_select_sound()
        
        app = App.get_running_app()
        col = {"q1": 4, "q2": 5, "q3": 6}[self.key]
        
        try:
            result = write_response(app.current_record_row, col, value)
            
            if result:
                self.manager.current = self.next_screen
            else:
                show_error_popup("エラー", "スプレッドシートへの書き込みに失敗しました")
                
        except Exception as e:
            show_error_popup("エラー", f"スプレッドシートへの書き込みに失敗しました: {e}")

class WelcomeScreen(Screen):
    """入室後の最終画面"""

    def on_enter(self):
        self.clear_widgets()
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation="vertical", padding=[80, 60, 80, 60], spacing=40)
        
        # ウェルカムラベル - エレガントなデザイン
        welcome_label = Label(
            text=f"ようこそ\n{App.get_running_app().student_name} さん",
            font_name=FONT_NAME,
            font_size="42sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            halign="center",
            valign="middle"
        )
        welcome_label.text_size = (None, None)
        layout.add_widget(welcome_label)
        
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 2)
        self.add_widget(layout)
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class GoodbyeScreen(Screen):
    """退室時画面"""

    def on_enter(self):
        self.clear_widgets()
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation="vertical", padding=[80, 60, 80, 60], spacing=40)
        
        # お別れラベル - エレガントなデザイン
        goodbye_label = Label(
            text=f"{App.get_running_app().student_name} さん\n\nまたね！",
            font_name=FONT_NAME,
            font_size="42sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            halign="center",
            valign="middle"
        )
        goodbye_label.text_size = (None, None)
        layout.add_widget(goodbye_label)
        
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "wait"), 2)
        self.add_widget(layout)
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SettingsScreen(Screen):
    """環境設定画面"""

    def __init__(self, **kw):
        super().__init__(**kw)
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # 入力フィールド設定
        self.output_folder_input = TextInput(
            multiline=False, 
            font_name=FONT_NAME, 
            font_size="18sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            padding=[10, 8]
        )
        self.ptouch_path_input = TextInput(
            multiline=False, 
            font_name=FONT_NAME, 
            font_size="18sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            padding=[10, 8]
        )

        # メインレイアウト - より整理されたデザイン
        main_layout = BoxLayout(orientation="vertical", padding=40, spacing=25)
        
        # タイトルヘッダー
        title_layout = BoxLayout(size_hint_y=None, height="60dp")
        title_label = Label(
            text="システム設定",
            font_name=FONT_NAME,
            font_size="32sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            halign="center"
        )
        title_label.text_size = (None, None)
        title_layout.add_widget(title_label)
        main_layout.add_widget(title_layout)

        # 出力フォルダパスセクション
        output_folder_section = BoxLayout(orientation="vertical", size_hint_y=None, height="100dp", spacing=8)
        output_folder_header = BoxLayout(size_hint_y=None, height="35dp", spacing=10)
        
        output_folder_label = Label(
            text="レポート出力フォルダパス",
            font_name=FONT_NAME,
            font_size="16sp",
            color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="middle",
            text_size=(None, None)
        )
        output_folder_header.add_widget(output_folder_label)
        
        output_folder_help_btn = Button(
            text="?",
            size_hint=(None, None),
            size=("35dp", "35dp"),
            font_name=FONT_NAME,
            font_size="14sp",
            background_color=(0.4, 0.7, 0.8, 1),  # 柔らかい水色
            color=(1, 1, 1, 1),
            background_normal=''
        )
        output_folder_help_btn.bind(on_release=self.show_output_folder_help)
        output_folder_header.add_widget(output_folder_help_btn)
        
        output_folder_section.add_widget(output_folder_header)
        output_folder_section.add_widget(self.output_folder_input)
        main_layout.add_widget(output_folder_section)
        
        # P-touch Editorパスセクション - カード風デザイン
        ptouch_section = BoxLayout(orientation="vertical", size_hint_y=None, height="100dp", spacing=8)
        ptouch_path_header = BoxLayout(size_hint_y=None, height="35dp", spacing=10)
        
        ptouch_label = Label(
            text="P-touch Editorパス",
            font_name=FONT_NAME,
            font_size="16sp",
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=0.5,
            halign="left"
        )
        ptouch_label.text_size = (None, None)
        ptouch_path_header.add_widget(ptouch_label)
        
        # P-touch Editor自動検索ボタン
        ptouch_auto_find_btn = Button(
            text="自動検索",
            size_hint=(None, 1),
            width=80,
            font_name=FONT_NAME,
            font_size="12sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        ptouch_auto_find_btn.bind(on_release=self.auto_find_ptouch_editor)
        ptouch_path_header.add_widget(ptouch_auto_find_btn)
        
        # P-touch Editorパスヘルプボタン
        ptouch_path_help_btn = Button(
            text="?",
            size_hint=(None, 1),
            width=30,
            font_name=FONT_NAME,
            font_size="14sp",
            background_color=(0.3, 0.6, 0.9, 1),  # エレガントブルー
            color=(1, 1, 1, 1),
            background_normal=''
        )
        ptouch_path_help_btn.bind(on_release=self.show_ptouch_path_help)
        ptouch_path_header.add_widget(ptouch_path_help_btn)
        
        ptouch_section.add_widget(ptouch_path_header)
        ptouch_section.add_widget(self.ptouch_path_input)
        main_layout.add_widget(ptouch_section)


        # スペーサー
        main_layout.add_widget(BoxLayout())

        # ボタンレイアウト - より洗練されたデザイン
        btn_layout = BoxLayout(size_hint_y=None, height="90dp", spacing=20, padding=[20, 10])
        
        save_btn = Button(
            text="保存",
            font_name=FONT_NAME,
            font_size="26sp",
            background_color=(0.5, 0.8, 0.6, 1),  # 柔らかい緑系
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        cancel_btn = Button(
            text="キャンセル",
            font_name=FONT_NAME,
            font_size="26sp",
            background_color=(0.6, 0.6, 0.6, 1),  # グレー系
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        main_layout.add_widget(btn_layout)

        self.add_widget(main_layout)

        save_btn.bind(on_release=self.on_save)
        cancel_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "wait"))
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    
    def show_ptouch_path_help(self, instance):
        title = "P-touch Editor実行ファイルパスの設定方法"
        message = (
            "【P-touch Editor実行ファイルパス】\n\n"
            "Brother P-touch Editorの実行ファイル（ptedit54.exe）の\n"
            "フルパスを設定してください。\n\n"
            "デフォルトのインストール場所：\n"
            "C:\\\\Program Files (x86)\\\\Brother\\\\Ptedit54\\\\ptedit54.exe\n\n"
            "または\n"
            "C:\\\\Program Files\\\\Brother\\\\Ptedit54\\\\ptedit54.exe\n\n"
            "注意事項：\n"
            "• Brother P-touch Editor 5.4がインストールされている必要があります\n"
            "• 正確なファイルパスを入力してください\n"
            "• パス区切り文字は \\\\\\\\ を使用してください（Windows）"
        )
        popup = HelpPopup(title, message)
        popup.open()
    
    def auto_find_ptouch_editor(self, instance):
        """クロスプラットフォーム対応のプリンター自動検索"""
        import threading
        
        def search_printer():
            printer_path = settings_manager.platform_config.find_printer_executable()
            
            # メインスレッドでUIを更新
            from kivy.clock import Clock
            if printer_path:
                Clock.schedule_once(lambda dt: self._update_ptouch_path(printer_path), 0)
                Clock.schedule_once(lambda dt: show_error_popup("検索結果", f"プリンターが見つかりました！\n{printer_path}"), 0)
            else:
                platform_info = settings_manager.platform_config.get_platform()
                Clock.schedule_once(lambda dt: show_error_popup("検索結果", f"{platform_info}環境でプリンターが見つかりませんでした。\n手動でパスを設定してください。"), 0)
        
        # 検索中メッセージを表示
        show_error_popup("検索中", "プリンターを検索中です...")
        
        # 別スレッドで検索実行
        threading.Thread(target=search_printer).start()
    
    def _update_ptouch_path(self, path):
        """検索結果でパスを更新する"""
        self.ptouch_path_input.text = path

    def show_output_folder_help(self, instance):
        title = "レポート出力フォルダパスの設定方法"
        message = (
            "【レポート出力フォルダパス】\n\n"
            "生成されたレポート（PDF/Excel）を保存する\n"
            "フォルダのパスを設定してください。\n\n"
            "例：\n"
            "C:\\\\Users\\\\ユーザー名\\\\Documents\\\\出席レポート\n"
            "output\\\\reports\n\n"
            "注意事項：\n"
            "• フォルダが存在しない場合は自動的に作成されます\n"
            "• 相対パス（例：output/reports）も使用できます\n"
            "• 絶対パスを推奨します（完全パス指定）\n"
            "• パス区切り文字は \\\\\\\\ または / を使用してください"
        )
        popup = HelpPopup(title, message)
        popup.open()

    def on_pre_enter(self, *_):
        data = load_settings()
        self.output_folder_input.text = data.get('output_directory', 'output/reports')
        self.ptouch_path_input.text = data.get('ptouch_editor_path', r'C:\Program Files (x86)\Brother\Ptedit54\ptedit54.exe')

    def on_save(self, *_):
        data = {
            'output_directory': self.output_folder_input.text.strip(),
            'ptouch_editor_path': self.ptouch_path_input.text.strip(),
        }
        save_settings(data)
        self.manager.current = "wait"


class LoadingScreen(Screen):
    def on_enter(self, *args):
        self.clear_widgets()
        
        # 背景色設定（エレガントなブルーテーマ）
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.96, 0.98, 1, 1)  # エレガントな薄いブルー背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation="vertical", padding=[80, 60, 80, 60], spacing=40)
        
        # ローディングラベル - エレガントなデザイン
        loading_label = Label(
            text="読み込み中...",
            font_name=FONT_NAME,
            font_size="38sp",
            color=(0.1, 0.1, 0.1, 1),  # 濃いグレー（統一テーマ）
            halign="center",
            valign="middle"
        )
        loading_label.text_size = (None, None)
        layout.add_widget(loading_label)
        
        self.add_widget(layout)
        
    def _update_rect(self, instance, value):
        """背景の矩形を更新"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size


# --- アプリ本体 ---
class AttendanceApp(App):
    def build(self):
        logger.info("Starting Attendance Management System v3.4")

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(WaitScreen(name="wait"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(LoadingScreen(name="loading"))
        sm.add_widget(PrintScreen(name="print_screen")) # PrintScreenを追加
        sm.add_widget(ReportScreen(name="report")) # ReportScreenを追加
        sm.add_widget(StudentRegistryScreen(name="student_registry")) # StudentRegistryScreenを追加
        sm.add_widget(GreetingScreen(name="greeting"))

        # 各質問画面
        sm.add_widget(
            QuestionScreen(
                key="q1",
                question="Q1.今日の気分は？",
                next_screen="q2",
                question_type="weather",
                name="q1",
            )
        )
        sm.add_widget(
            QuestionScreen(
                key="q2",
                question="Q2.昨日の睡眠の満足度は？",
                next_screen="q3",
                question_type="sleep",
                name="q2",
            )
        )
        sm.add_widget(
            QuestionScreen(
                key="q3",
                question="Q3.今日は何しに来た？",
                next_screen="welcome",
                question_type="purpose",
                name="q3",
            )
        )

        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(GoodbyeScreen(name="goodbye"))
        return sm




# === ここから追記 ==========================================
def main() -> None:
    """
    CLI エントリポイント.
    `python -m attendance_app` から呼ばれる。
    """
    # 既存の GUI 起動処理を呼び出す
    AttendanceApp().run()


if __name__ == "__main__":  # 単体実行も可能にしておく
    main()
# === ここまで追記 ==========================================