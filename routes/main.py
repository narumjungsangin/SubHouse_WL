from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.contract import Contract

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """메인 페이지 렌더링"""
    # 데이터베이스에서 모든 매물 가져오기
    try:
        contracts = Contract.query.order_by(Contract.created.desc()).all()
    except Exception as e:
        # 오류 발생 시 빈 리스트로 처리
        contracts = []
    return render_template("index.html", contracts=contracts)


@main_bp.route("/add", methods=["POST"])
def add_contract():
    """새 매물 추가"""
    return redirect(url_for("main.index"))


@main_bp.route("/mobile-menu")
def mobile_menu():
    """모바일 메뉴 렌더링"""
    return render_template("partials/mobile_menu.html")
