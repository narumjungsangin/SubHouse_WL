from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    current_app,
    request,
    flash,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from authlib.integrations.flask_client import OAuth
import json
import requests
from models import db
from models.user import User

# Auth 블루프린트 생성
auth_bp = Blueprint("auth", __name__)

# OAuth 객체 초기화
oauth = OAuth()


def init_login_manager(app):
    """로그인 매니저 초기화"""
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def init_oauth(app):
    """OAuth 초기화"""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
        client_kwargs={"scope": "openid email profile"},
    )


def get_google_provider_cfg():
    """Google Provider 설정 가져오기"""
    return requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()


@auth_bp.route("/login")
def login():
    """로그인 페이지"""
    # 로그인 디버깅용 로깅
    current_app.logger.info(f"Login route accessed, args: {request.args}")

    # 사용자가 이미 로그인한 경우 메인 페이지로 리디렉션
    if current_user.is_authenticated:
        current_app.logger.info(f"User already logged in: {current_user.name}")
        return redirect(url_for("main.index"))

    # next 파라미터가 있으면 세션에 저장
    next_url = None
    if request.args.get("next"):
        next_url = request.args.get("next")
        session["next"] = next_url
        # 세션 상태 확인
        current_app.logger.info(f"Saved next URL to session: {next_url}")
        current_app.logger.info(f"Session after save: {session}")

    # Google 로그인으로 리다이렉트 (쉷션 대신 쿼리 파라미터로 next 전달)
    if next_url:
        return redirect(url_for("auth.google_login", next=next_url))
    else:
        return redirect(url_for("auth.google_login"))


@auth_bp.route("/login/google")
def google_login():
    """Google 로그인 시작"""
    # next 파라미터가 URL에 있는 경우도 처리
    if request.args.get("next"):
        session["next"] = request.args.get("next")
        current_app.logger.info(
            f"Saved next URL from google_login: {session.get('next')}"
        )

    redirect_uri = url_for("auth.google_callback", _external=True)
    current_app.logger.info(f"Starting Google OAuth with redirect_uri: {redirect_uri}")
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/callback")
def google_callback():
    """Google OAuth 콜백 처리"""
    try:
        # 콜백 디버깅용 로깅
        current_app.logger.info("Google OAuth callback received")

        token = oauth.google.authorize_access_token()
        current_app.logger.info("Google access token authorized successfully")

        # ID 토큰 파싱 대신 userinfo 엔드포인트 사용
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        current_app.logger.info(f"Requesting user info from: {userinfo_endpoint}")
        resp = oauth.google.get(userinfo_endpoint, token=token)
        user_info = resp.json()
        current_app.logger.info(f"User info response: {user_info}")
        
        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name", email.split("@")[0] if email else "사용자")
        profile_picture = user_info.get("picture")

        current_app.logger.info(
            f"Google user info received: email={email}, name={name}"
        )

        # 기존 사용자 검색 또는 새 사용자 생성
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # 기존 이메일이 있는 경우 Google ID 업데이트
                current_app.logger.info(
                    f"Updating existing user with Google ID: {email}"
                )
                user.google_id = google_id
                user.profile_picture = profile_picture
            else:
                # 새 사용자 생성
                current_app.logger.info(f"Creating new user: {email}")
                user = User(
                    google_id=google_id,
                    email=email,
                    name=name,
                    profile_picture=profile_picture,
                    account_status="active",
                )
                db.session.add(user)
            db.session.commit()
        else:
            current_app.logger.info(f"Existing user found: {email}")

        # 사용자 로그인
        login_user(user)
        current_app.logger.info(f"User logged in: {user.name} (id: {user.id})")

        # HTMX 요청인 경우 부분 응답
        if request.headers.get("HX-Request"):
            current_app.logger.info("Returning HTMX partial response")
            return render_template("partials/user_nav.html")

        # 원래 요청한 페이지가 있으면 해당 페이지로, 없으면 메인 페이지로
        # 세션에서 next 값 가져오기 전에 로깅
        current_app.logger.info(f"Session contents before redirect: {session}")

        next_page = None
        if "next" in session:
            next_page = session.get("next")
            current_app.logger.info(f"Found next URL in session: {next_page}")
            session.pop("next", None)

        if not next_page:
            next_page = url_for("main.index")
            current_app.logger.info(f"No next URL found, redirecting to main page")

        current_app.logger.info(f"Final redirect destination: {next_page}")
        return redirect(next_page)

    except Exception as e:
        current_app.logger.error(f"Google login error: {str(e)}")
        current_app.logger.exception("Detailed error traceback:")
        flash("구글 로그인 중 오류가 발생했습니다. 다시 시도해주세요.", "error")
        return redirect(url_for("main.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    """로그아웃"""
    logout_user()

    # HTMX 요청인 경우 부분 응답
    if request.headers.get("HX-Request"):
        return render_template("partials/user_nav.html")

    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    """사용자 프로필 페이지"""
    return render_template("auth/profile.html", user=current_user)
