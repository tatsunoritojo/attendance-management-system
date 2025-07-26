from pathlib import Path
from typing import Dict, Any
import jinja2
import calendar


def render_bar_chart(value: int, max_value: int, width: int = 5) -> str:
    """
    視覚的におしゃれなバーチャートを生成
    例: render_bar_chart(3, 5) → "●●●○○"
    """
    if max_value == 0:
        return "○" * width
    
    filled_blocks = int((value / max_value) * width)
    empty_blocks = width - filled_blocks
    
    # よりおしゃれな記号を使用
    return "●" * filled_blocks + "○" * empty_blocks


def render_colored_bar_chart(value: int, max_value: int, width: int = 5, category: str = "default") -> str:
    """
    カテゴリに応じて色付きバーチャートを生成
    """
    if max_value == 0:
        return "○" * width
    
    filled_blocks = int((value / max_value) * width)
    empty_blocks = width - filled_blocks
    
    # カテゴリに応じて異なる記号を使用
    if category == "mood":
        filled_symbol = "🌟"
        empty_symbol = "⭐"
    elif category == "sleep":
        filled_symbol = "💤"
        empty_symbol = "💭"
    elif category == "purpose":
        filled_symbol = "📚"
        empty_symbol = "📖"
    else:
        filled_symbol = "●"
        empty_symbol = "○"
    
    return filled_symbol * filled_blocks + empty_symbol * empty_blocks


def format_date_japanese(date_str: str) -> str:
    """
    日付文字列を日本語形式に変換
    例: "2025-07-15" → "07/15 (月)"
    """
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[dt.weekday()]
        return f"{dt.month:02d}/{dt.day:02d} ({weekday})"
    except ValueError:
        return date_str


def get_template_directory() -> Path:
    """テンプレートディレクトリのパスを取得"""
    return Path(__file__).parent.parent / "templates"


def load_template(template_name: str) -> jinja2.Template:
    """HTMLテンプレートを読み込み"""
    template_dir = get_template_directory()
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = jinja2.Template(template_content)
    return template


def render_report_html(data: Dict[str, Any]) -> str:
    """データをHTMLテンプレートに適用"""
    template = load_template("monthly_report.html")
    
    # Calculate max attendance for bar chart scaling
    max_attendance = max(data["attendance_count"], 1)
    
    # Prepare data for template
    template_data = {
        "student_name": data["student_name"],
        "year": data.get("year", 2025),
        "month": data.get("month", 1),
        "attendance_count": data["attendance_count"],
        "average_stay_minutes": data["average_stay_minutes"],
        "daily_records": data["daily_records"],
        "mood_distribution": data["mood_distribution"],
        "sleep_stats": data["sleep_stats"],
        "purpose_distribution": data["purpose_distribution"],
        "max_attendance": max_attendance
    }
    
    # Add custom filters
    template.globals.update({
        "render_bar_chart": render_bar_chart,
        "format_date_japanese": format_date_japanese
    })
    
    return template.render(**template_data)


def create_template_with_styles() -> str:
    """完整なHTMLテンプレート（CSS埋め込み）を生成"""
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Onedrop 月次レポート</title>
    <style>
        @page {
            size: A4;
            margin: 20mm 15mm;
        }
        
        body { 
            font-family: "UDDigiKyokashoN-R", "Meiryo", "MS Gothic", sans-serif; 
            font-size: 12px; 
            line-height: 1.4;
            margin: 0;
            padding: 0;
            color: #333;
        }
        
        .header { 
            text-align: center; 
            border-bottom: 2px solid #333; 
            padding: 15px; 
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 20px;
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        
        .header p {
            font-size: 14px;
            margin: 5px 0;
            color: #555;
        }
        
        .section { 
            margin: 20px 0; 
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fafafa;
        }
        
        .section h3 { 
            margin: 0 0 15px 0; 
            color: #2c3e50;
            font-size: 16px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }
        
        .stats-row { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 3px;
        }
        
        .stats-row span {
            font-weight: bold;
            color: #34495e;
        }
        
        .bar-chart { 
            font-family: "MS Gothic", monospace; 
            font-size: 16px;
            line-height: 1.8;
            margin: 10px 0;
        }
        
        .bar-chart .bar-row {
            display: flex;
            align-items: center;
            margin: 8px 0;
        }
        
        .bar-chart .bar {
            margin-right: 10px;
            min-width: 80px;
        }
        
        .bar-fill { 
            color: #3498db; 
            font-weight: bold;
        }
        
        .bar-empty { 
            color: #bdc3c7; 
        }
        
        .attendance-record { 
            margin: 5px 0; 
            padding: 5px 10px;
            font-size: 11px;
            background-color: #fff;
            border-left: 3px solid #3498db;
        }
        
        .attendance-record:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .sleep-average {
            font-size: 14px;
            font-weight: bold;
            color: #8e44ad;
            margin-bottom: 10px;
        }
        
        .no-records {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Onedrop 月次レポート</h1>
        <p>生徒名: {{ student_name }} | 対象期間: {{ year }}年{{ month }}月</p>
    </div>

    <div class="section">
        <h3>📈 出席状況</h3>
        <div class="stats-row">
            <span>出席日数: {{ attendance_count }}日</span>
            <span>平均滞在時間: {{ average_stay_minutes }}分</span>
        </div>
    </div>

    <div class="section">
        <h3>📅 出席詳細</h3>
        {% if daily_records %}
            {% for record in daily_records %}
            <div class="attendance-record">
                {{ format_date_japanese(record.date) }} {{ record.entry_time }}-{{ record.exit_time }} ({{ record.stay_minutes }}分)
            </div>
            {% endfor %}
        {% else %}
            <div class="no-records">この月の出席記録はありません</div>
        {% endif %}
    </div>

    <div class="section">
        <h3>😊 気分の様子</h3>
        <div class="bar-chart">
            {% for mood, count in mood_distribution.items() %}
            <div class="bar-row">
                <span class="bar">{{ render_bar_chart(count, max_attendance) }}</span>
                <span>{{ mood }} ({{ count }}回)</span>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="section">
        <h3>😴 睡眠の状況</h3>
        <div class="sleep-average">平均: {{ sleep_stats.average_percentage }}％</div>
        <div class="bar-chart">
            {% for range, count in sleep_stats.distribution.items() %}
            <div class="bar-row">
                <span class="bar">{{ render_bar_chart(count, max_attendance) }}</span>
                <span>{{ range }} ({{ count }}回)</span>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="section">
        <h3>🎯 来塾の目的</h3>
        <div class="bar-chart">
            {% for purpose, count in purpose_distribution.items() %}
            <div class="bar-row">
                <span class="bar">{{ render_bar_chart(count, max_attendance) }}</span>
                <span>{{ purpose }} ({{ count }}回)</span>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>'''