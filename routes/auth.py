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

    # Google 로그인으로 리다이렉트 (세션 대신 쿼리 파라미터로 next 전달)
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

        # userinfo 엔드포인트 호출
        response = requests.get(userinfo_endpoint, headers={
            'Authorization': f'Bearer {token["access_token"]}'
        })
        response.raise_for_status()
        user_info = response.json()

        # 사용자 정보 로깅
        current_app.logger.info(f"User info received: {json.dumps(user_info, indent=2)}")

        # 사용자 정보에서 이메일과 이름 추출
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")

        # 사용자 정보 로깅
        current_app.logger.info(f"User email: {email}, name: {name}")

        # 사용자 정보 저장
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                profile_picture=picture,
                google_id=user_info.get("sub")
            )
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"New user created: {email}")
        else:
            current_app.logger.info(f"Existing user logged in: {email}")

        # 로그인 처리
        login_user(user)
        current_app.logger.info(f"User logged in successfully: {email}")

        # next URL 처리
        # 쿼리 파라미터로 전달된 next URL 확인
        next_url = request.args.get("next")
        if next_url:
            current_app.logger.info(f"Next URL from query parameter: {next_url}")
            # next URL이 세션에 저장되어 있는지 확인
            session_next = session.get("next")
            if session_next:
                current_app.logger.info(f"Session next URL: {session_next}")
                # 쿼리 파라미터로 전달된 URL이 더 우선
                session["next"] = next_url
                current_app.logger.info(f"Updated session next URL to: {next_url}")

        # 세션에서 next URL 가져오기
        next_page = session.get("next")
        current_app.logger.info(f"Retrieved next URL from session: {next_page}")

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


@auth_bp.route("/about")
def about():
    """회사소개 페이지"""
    return render_template("aboutUs.html")
