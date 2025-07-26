"""
名簿情報登録画面
出席管理システム用の学生情報管理画面
"""

import csv
import logging
import os
from pathlib import Path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

from attendance_app.path_manager import get_asset_path
from attendance_app.spreadsheet import _read_student_data_from_excel
from attendance_app.student_data_manager import student_data_manager
from kivy.uix.spinner import Spinner

logger = logging.getLogger(__name__)

# フォント設定を動的に取得（font_manager.pyの関数を利用）
try:
    from attendance_app.font_manager import register_font
    FONT_AVAILABLE, FONT_NAME = register_font()
except ImportError:
    # フォールバック
    FONT_AVAILABLE, FONT_NAME = False, "Roboto"

class StudentRegistryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 背景色設定（エレガントなブルーテーマ）
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
        
        # タイトル
        title_label = Label(
            text="名簿情報管理", 
            font_name=FONT_NAME, 
            font_size="36sp", 
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, 
            height="80dp"
        )
        main_layout.add_widget(title_label)

        # 新規登録セクション
        registration_section = self.create_registration_section()
        main_layout.add_widget(registration_section)

        # 学生一覧セクション
        students_section = self.create_students_list_section()
        main_layout.add_widget(students_section)

        # 戻るボタン
        back_button = Button(
            text="メインメニューに戻る", 
            font_name=FONT_NAME, 
            size_hint_y=None, 
            height="50dp",
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        back_button.bind(on_press=lambda *_: setattr(self.manager, "current", "wait"))
        main_layout.add_widget(back_button)
        
        self.add_widget(main_layout)

    def create_registration_section(self):
        """新規学生登録セクション"""
        section = BoxLayout(orientation="vertical", size_hint_y=None, height="400dp", spacing=10)
        
        # セクションタイトル
        section_title = Label(
            text="新規学生登録",
            font_name=FONT_NAME,
            font_size="24sp",
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height="40dp"
        )
        section.add_widget(section_title)
        
        # 入力フィールドコンテナ
        inputs_container = BoxLayout(orientation="vertical", spacing=8)
        
        # 生徒氏名入力
        student_name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=10)
        student_name_layout.add_widget(Label(text="生徒氏名:", font_name=FONT_NAME, size_hint_x=None, width="120dp", color=(0.1, 0.1, 0.1, 1)))
        self.student_name_input = TextInput(
            multiline=False,
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        student_name_layout.add_widget(self.student_name_input)
        inputs_container.add_widget(student_name_layout)
        
        # 保護者氏名入力
        guardian_name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=10)
        guardian_name_layout.add_widget(Label(text="保護者氏名:", font_name=FONT_NAME, size_hint_x=None, width="120dp", color=(0.1, 0.1, 0.1, 1)))
        self.guardian_name_input = TextInput(
            multiline=False,
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        guardian_name_layout.add_widget(self.guardian_name_input)
        inputs_container.add_widget(guardian_name_layout)
        
        # 保護者連絡先入力
        guardian_contact_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=10)
        guardian_contact_layout.add_widget(Label(text="保護者連絡先:", font_name=FONT_NAME, size_hint_x=None, width="120dp", color=(0.1, 0.1, 0.1, 1)))
        self.guardian_contact_input = TextInput(
            multiline=False,
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        guardian_contact_layout.add_widget(self.guardian_contact_input)
        inputs_container.add_widget(guardian_contact_layout)
        
        # 学校名入力
        school_name_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=10)
        school_name_layout.add_widget(Label(text="学校名:", font_name=FONT_NAME, size_hint_x=None, width="120dp", color=(0.1, 0.1, 0.1, 1)))
        self.school_name_input = TextInput(
            multiline=False,
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        school_name_layout.add_widget(self.school_name_input)
        inputs_container.add_widget(school_name_layout)
        
        # 生年月日入力（年・月・日選択式）
        birth_date_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=10)
        birth_date_layout.add_widget(Label(text="生年月日:", font_name=FONT_NAME, size_hint_x=None, width="120dp", color=(0.1, 0.1, 0.1, 1)))
        
        # 年選択
        current_year = 2025
        years = [str(y) for y in range(1950, current_year + 1)]
        years.reverse()  # 新しい年を上に
        self.year_spinner = Spinner(
            text="年",
            values=years,
            size_hint_x=None,
            width="80dp",
            font_name=FONT_NAME
        )
        birth_date_layout.add_widget(self.year_spinner)
        birth_date_layout.add_widget(Label(text="年", font_name=FONT_NAME, size_hint_x=None, width="30dp", color=(0.1, 0.1, 0.1, 1)))
        
        # 月選択
        months = [str(m) for m in range(1, 13)]
        self.month_spinner = Spinner(
            text="月",
            values=months,
            size_hint_x=None,
            width="60dp",
            font_name=FONT_NAME
        )
        birth_date_layout.add_widget(self.month_spinner)
        birth_date_layout.add_widget(Label(text="月", font_name=FONT_NAME, size_hint_x=None, width="30dp", color=(0.1, 0.1, 0.1, 1)))
        
        # 日選択
        days = [str(d) for d in range(1, 32)]
        self.day_spinner = Spinner(
            text="日",
            values=days,
            size_hint_x=None,
            width="60dp",
            font_name=FONT_NAME
        )
        birth_date_layout.add_widget(self.day_spinner)
        birth_date_layout.add_widget(Label(text="日", font_name=FONT_NAME, size_hint_x=None, width="30dp", color=(0.1, 0.1, 0.1, 1)))
        
        inputs_container.add_widget(birth_date_layout)
        
        section.add_widget(inputs_container)
        
        # ボタンレイアウト
        button_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", spacing=10)
        
        # 登録ボタン
        register_button = Button(
            text="登録",
            font_name=FONT_NAME,
            background_color=(0.5, 0.8, 0.6, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        register_button.bind(on_press=self.register_student)
        button_layout.add_widget(register_button)
        
        # クリアボタン
        clear_button = Button(
            text="入力クリア",
            font_name=FONT_NAME,
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        clear_button.bind(on_press=self.clear_inputs)
        button_layout.add_widget(clear_button)
        
        section.add_widget(button_layout)
        
        return section

    def create_students_list_section(self):
        """学生一覧表示セクション"""
        section = BoxLayout(orientation="vertical", spacing=10)
        
        # セクションヘッダー
        header_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", spacing=10)
        
        section_title = Label(
            text="登録済み学生一覧",
            font_name=FONT_NAME,
            font_size="24sp",
            color=(0.1, 0.1, 0.1, 1),
            size_hint_x=0.7
        )
        header_layout.add_widget(section_title)
        
        # リフレッシュボタン
        refresh_button = Button(
            text="リストを更新",
            font_name=FONT_NAME,
            size_hint_x=0.3,
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        refresh_button.bind(on_press=self.refresh_students_list)
        header_layout.add_widget(refresh_button)
        
        section.add_widget(header_layout)
        
        # 学生リストのスクロールビュー
        self.students_list_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.students_list_layout.bind(minimum_height=self.students_list_layout.setter('height'))
        
        scroll = ScrollView()
        scroll.add_widget(self.students_list_layout)
        section.add_widget(scroll)
        
        # 初期データをロード
        self.refresh_students_list()
        
        return section

    def refresh_students_list(self, instance=None):
        """学生リストを更新（StudentsListシートからデータを表示）"""
        self.students_list_layout.clear_widgets()
        
        try:
            # StudentsListシートからデータを取得
            student_list_data = student_data_manager.get_student_list_data()
            
            if not student_list_data:
                no_data_label = Label(
                    text="登録されている学生がいません",
                    font_name=FONT_NAME,
                    size_hint_y=None,
                    height="40dp",
                    color=(0.1, 0.1, 0.1, 1)
                )
                self.students_list_layout.add_widget(no_data_label)
                return
            
            # ヘッダー行
            header_layout = BoxLayout(size_hint_y=None, height="40dp", spacing=5)
            header_layout.add_widget(Label(
                text="生徒氏名",
                font_name=FONT_NAME,
                font_size="16sp",
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.2,
                bold=True
            ))
            header_layout.add_widget(Label(
                text="保護者氏名",
                font_name=FONT_NAME,
                font_size="16sp",
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.2,
                bold=True
            ))
            header_layout.add_widget(Label(
                text="保護者連絡先",
                font_name=FONT_NAME,
                font_size="16sp",
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.2,
                bold=True
            ))
            header_layout.add_widget(Label(
                text="学校名",
                font_name=FONT_NAME,
                font_size="16sp",
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.2,
                bold=True
            ))
            header_layout.add_widget(Label(
                text="登録日",
                font_name=FONT_NAME,
                font_size="16sp",
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.2,
                bold=True
            ))
            self.students_list_layout.add_widget(header_layout)
            
            # StudentsListシートのデータを表示
            for student in student_list_data:
                student_layout = BoxLayout(size_hint_y=None, height="40dp", spacing=5)
                
                # 生徒氏名
                student_layout.add_widget(Label(
                    text=student['student_name'],
                    font_name=FONT_NAME,
                    color=(0.1, 0.1, 0.1, 1),
                    size_hint_x=0.2
                ))
                
                # 保護者氏名
                student_layout.add_widget(Label(
                    text=student['guardian_name'],
                    font_name=FONT_NAME,
                    color=(0.1, 0.1, 0.1, 1),
                    size_hint_x=0.2
                ))
                
                # 保護者連絡先
                student_layout.add_widget(Label(
                    text=student['guardian_contact'],
                    font_name=FONT_NAME,
                    color=(0.1, 0.1, 0.1, 1),
                    size_hint_x=0.2
                ))
                
                # 学校名
                student_layout.add_widget(Label(
                    text=student['school_name'],
                    font_name=FONT_NAME,
                    color=(0.1, 0.1, 0.1, 1),
                    size_hint_x=0.2
                ))
                
                # 登録日
                registration_date = student['registration_date'][:10] if len(student['registration_date']) > 10 else student['registration_date']
                student_layout.add_widget(Label(
                    text=registration_date,
                    font_name=FONT_NAME,
                    color=(0.1, 0.1, 0.1, 1),
                    size_hint_x=0.2
                ))
                
                self.students_list_layout.add_widget(student_layout)
                
        except Exception as e:
            logger.error(f"Error refreshing students list: {e}")
            error_label = Label(
                text=f"学生リストの読み込みに失敗しました: {e}",
                font_name=FONT_NAME,
                size_hint_y=None,
                height="40dp",
                color=(0.8, 0.2, 0.2, 1)
            )
            self.students_list_layout.add_widget(error_label)

    def register_student(self, instance):
        """学生を登録"""
        # 入力値を取得
        student_name = self.student_name_input.text.strip()
        guardian_name = self.guardian_name_input.text.strip()
        guardian_contact = self.guardian_contact_input.text.strip()
        school_name = self.school_name_input.text.strip()
        
        # 必須フィールドの検証
        if not student_name:
            self.show_popup("エラー", "生徒氏名を入力してください。")
            return
        
        if not guardian_name:
            self.show_popup("エラー", "保護者氏名を入力してください。")
            return
        
        if not guardian_contact:
            self.show_popup("エラー", "保護者連絡先を入力してください。")
            return
        
        if not school_name:
            self.show_popup("エラー", "学校名を入力してください。")
            return
            
        # 生年月日の検証
        year = self.year_spinner.text
        month = self.month_spinner.text
        day = self.day_spinner.text
        
        if year == "年" or month == "月" or day == "日":
            self.show_popup("エラー", "生年月日を選択してください。")
            return
        
        try:
            # 学生データを作成
            birth_date_str = f"{year}/{month.zfill(2)}/{day.zfill(2)}"
            student_data = {
                'student_name': student_name,
                'guardian_name': guardian_name,
                'guardian_contact': guardian_contact,
                'school_name': school_name,
                'birth_date': birth_date_str
            }
            
            # 学生を登録
            success, student_id, error_msg = student_data_manager.register_new_student(student_data)
            
            if success:
                self.show_success_popup(student_name, student_id)
                self.clear_inputs()
                self.refresh_students_list()
            else:
                self.show_popup("エラー", error_msg if error_msg else "学生の登録に失敗しました。")
                
        except Exception as e:
            logger.error(f"Error registering student: {e}")
            self.show_popup("エラー", f"学生の登録中にエラーが発生しました: {e}")

    def delete_student(self, student_id):
        """学生を削除"""
        try:
            # 確認ダイアログ
            self.confirm_delete(student_id)
            
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            self.show_popup("エラー", f"学生の削除に失敗しました: {e}")

    def confirm_delete(self, student_id):
        """削除確認ダイアログ"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        # 確認メッセージ
        message = Label(
            text=f"学生ID「{student_id}」を削除しますか？\nこの操作は元に戻せません。",
            font_name=FONT_NAME,
            font_size="18sp",
            color=(0.1, 0.1, 0.1, 1),
            halign="center",
            valign="middle"
        )
        message.text_size = (400, None)
        content.add_widget(message)
        
        # ボタンレイアウト
        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height="50dp")
        
        # キャンセルボタン
        cancel_btn = Button(
            text="キャンセル",
            font_name=FONT_NAME,
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        # 削除ボタン
        delete_btn = Button(
            text="削除する",
            font_name=FONT_NAME,
            background_color=(0.8, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)
        
        # ポップアップ作成
        popup = Popup(
            title="削除の確認",
            content=content,
            size_hint=(0.8, 0.6),
            title_font=FONT_NAME,
            auto_dismiss=False
        )
        
        # ボタンのイベント設定
        cancel_btn.bind(on_release=popup.dismiss)
        delete_btn.bind(on_release=lambda x: self.execute_delete(student_id, popup))
        
        popup.open()

    def execute_delete(self, student_id, popup):
        """実際の削除処理"""
        try:
            # CSVファイルから削除
            csv_file_path = get_asset_path('sample_data.csv')
            temp_file_path = csv_file_path.parent / 'temp_sample_data.csv'
            
            with open(csv_file_path, 'r', encoding='utf-8') as infile, \
                 open(temp_file_path, 'w', newline='', encoding='utf-8') as outfile:
                
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                for row in reader:
                    if len(row) >= 2 and row[0] != student_id:
                        writer.writerow(row)
            
            # 元のファイルを新しいファイルで置き換え
            os.replace(temp_file_path, csv_file_path)
            
            popup.dismiss()
            self.show_popup("成功", f"学生ID「{student_id}」を削除しました。")
            self.refresh_students_list()
            
        except Exception as e:
            logger.error(f"Error executing delete: {e}")
            popup.dismiss()
            self.show_popup("エラー", f"学生の削除に失敗しました: {e}")

    def clear_inputs(self, instance=None):
        """入力フィールドをクリア"""
        self.student_name_input.text = ""
        self.guardian_name_input.text = ""
        self.guardian_contact_input.text = ""
        self.school_name_input.text = ""
        self.year_spinner.text = "年"
        self.month_spinner.text = "月"
        self.day_spinner.text = "日"

    def show_popup(self, title, message):
        """メッセージポップアップを表示"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # メッセージラベル
        content_label = Label(
            text=message,
            font_name=FONT_NAME,
            font_size="18sp",
            color=(0.2, 0.2, 0.2, 1),
            halign="center",
            valign="middle"
        )
        content_label.text_size = (400, None)
        content.add_widget(content_label)
        
        # 閉じるボタン
        close_btn = Button(
            text="確認",
            size_hint_y=None,
            height="50dp",
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(0.4, 0.7, 0.8, 1),
            color=(1, 1, 1, 1),
            background_normal=''
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5),
            title_font=FONT_NAME,
            auto_dismiss=False
        )
        
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def show_success_popup(self, student_name, student_id):
        """登録成功メッセージポップアップを表示"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # 成功メッセージラベル
        success_message = f"《{student_name}》さんを登録しました\n\n学籍番号: {student_id}"
        content_label = Label(
            text=success_message,
            font_name=FONT_NAME,
            font_size="20sp",
            color=(0.1, 0.6, 0.1, 1),  # 緑色
            halign="center",
            valign="middle"
        )
        content_label.text_size = (400, None)
        content.add_widget(content_label)
        
        # 確認ボタン
        close_btn = Button(
            text="確認",
            size_hint_y=None,
            height="50dp",
            font_name=FONT_NAME,
            font_size="16sp",
            background_color=(0.5, 0.8, 0.6, 1),  # 緑系
            color=(1, 1, 1, 1),
            background_normal=''
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="登録完了",
            content=content,
            size_hint=(0.8, 0.5),
            title_font=FONT_NAME,
            auto_dismiss=False
        )
        
        close_btn.bind(on_release=popup.dismiss)
        popup.open()