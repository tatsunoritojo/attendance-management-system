from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase

# フォント利用可能性をチェック
try:
    LabelBase.register(name="UDDigiKyokashoN-R", fn_regular="dummy")
    FONT_AVAILABLE = False
except:
    FONT_AVAILABLE = False

# フォント登録の確認
def check_font_available():
    try:
        from importlib import resources as res
        with res.path("src.attendance_app.assets.fonts", "UDDigiKyokashoN-R.ttc") as p:
            LabelBase.register(name="UDDigiKyokashoN-R", fn_regular=str(p))
            return True
    except:
        return False

FONT_AVAILABLE = check_font_available()

class PrintDialog(Popup):
    def __init__(self, student_name: str, on_confirm, on_cancel, **kwargs):
        super().__init__(**kwargs)
        self.title = '印刷確認'
        self.title_font = "UDDigiKyokashoN-R" if FONT_AVAILABLE else "Roboto"
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = False
        
        # ダイアログ背景色設定
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)  # 薄いグレー背景
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda instance, value: setattr(self.bg_rect, 'size', value))
        self.bind(pos=lambda instance, value: setattr(self.bg_rect, 'pos', value))
        
        layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # メッセージラベル - より目立つデザイン
        message_label = Label(
            text=f'{student_name}さんのラベルを印刷しますか？',
            font_name="UDDigiKyokashoN-R" if FONT_AVAILABLE else "Roboto",
            font_size="20sp",
            color=(1, 1, 1, 1),  # 白文字
            halign="center",
            valign="middle"
        )
        message_label.text_size = (None, None)
        layout.add_widget(message_label)
        
        # ボタンレイアウト - より洗練されたデザイン
        btn_layout = BoxLayout(size_hint_y=None, height="60dp", spacing=20)
        
        # 印刷ボタン - 柔らかい緑系
        ok_btn = Button(
            text='印刷実行',
            font_name="UDDigiKyokashoN-R" if FONT_AVAILABLE else "Roboto",
            font_size="18sp",
            background_color=(0.5, 0.8, 0.6, 1),  # 柔らかい緑系
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        
        # キャンセルボタン - グレー系
        cancel_btn = Button(
            text='キャンセル',
            font_name="UDDigiKyokashoN-R" if FONT_AVAILABLE else "Roboto",
            font_size="18sp",
            background_color=(0.6, 0.6, 0.6, 1),  # グレー系
            color=(1, 1, 1, 1),  # 白文字
            background_normal=''
        )
        
        btn_layout.add_widget(ok_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        self.content = layout
        ok_btn.bind(on_release=lambda *_: (on_confirm(), self.dismiss()))
        cancel_btn.bind(on_release=lambda *_: (on_cancel(), self.dismiss()))