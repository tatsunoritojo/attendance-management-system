import json
from pathlib import Path
from typing import Dict, Any

def load_report_template() -> Dict[str, Any]:
    """レポートテンプレート設定を読み込む"""
    template_path = Path(__file__).parent.parent / "templates" / "report_config.json"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # デフォルト設定を返す
        return get_default_template()
    except json.JSONDecodeError as e:
        print(f"テンプレートファイルの読み込みエラー: {e}")
        return get_default_template()

def get_default_template() -> Dict[str, Any]:
    """デフォルトのテンプレート設定を取得"""
    return {
        "report_title": "Onedrop 月次レポート",
        "sections": {
            "attendance_status": {
                "title": "■ 出席状況",
                "enabled": True,
                "show_calendar": True,
                "position": 1
            },
            "attendance_details": {
                "title": "■ 出席詳細",
                "enabled": True,
                "show_individual_records": True,
                "position": 2
            },
            "mood_analysis": {
                "title": "■ 気分の様子",
                "enabled": True,
                "show_images": True,
                "position": 3
            },
            "sleep_analysis": {
                "title": "■ 睡眠の状況",
                "enabled": True,
                "show_images": True,
                "show_average": False,
                "position": 4
            },
            "purpose_analysis": {
                "title": "■ 来塾の目的",
                "enabled": True,
                "show_images": True,
                "position": 5
            },
            "monthly_summary": {
                "title": "■ 月次サマリー",
                "enabled": True,
                "show_trends": True,
                "position": 6
            },
            "goals_achievements": {
                "title": "■ 目標と達成度",
                "enabled": True,
                "show_progress": True,
                "position": 7
            },
            "feedback_comments": {
                "title": "■ フィードバック・コメント",
                "enabled": True,
                "show_teacher_comments": True,
                "position": 8
            },
            "improvement_suggestions": {
                "title": "■ 改善提案",
                "enabled": True,
                "show_recommendations": True,
                "position": 9
            },
            "next_month_plan": {
                "title": "■ 来月の計画",
                "enabled": True,
                "show_schedule": True,
                "position": 10
            }
        },
        "formatting": {
            "fonts": {
                "title_size": 18,
                "heading_size": 13,
                "normal_size": 10,
                "stats_size": 11
            },
            "spacing": {
                "section_spacing": 0.3,
                "paragraph_spacing": 0.3,
                "calendar_spacing": 0.2
            }
        },
        "images": {
            "uploaded": [],
            "settings": {
                "position": "background",
                "width": 50,
                "opacity": 30,
                "alignment": "center",
                "x": 10,
                "y": 10
            }
        },
        "colors": {
            "title_color": "#2c3e50",
            "heading_color": "#2c3e50",
            "stats_color": "#34495e",
            "separator_color": "#333333"
        },
        "layout": {
            "page_orientation": "portrait",
            "column_count": 1,
            "sections_per_page": 5
        }
    }

def save_report_template(template: Dict[str, Any]) -> bool:
    """レポートテンプレート設定を保存する"""
    template_path = Path(__file__).parent.parent / "templates" / "report_config.json"
    
    try:
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"テンプレートファイルの保存エラー: {e}")
        return False

def get_template_path() -> Path:
    """テンプレートファイルのパスを取得"""
    return Path(__file__).parent.parent / "templates" / "report_config.json"