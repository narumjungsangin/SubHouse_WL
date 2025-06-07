from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
from sqlalchemy import or_, and_, desc, func
from wtforms import StringField, IntegerField, FloatField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Optional
from models import db
from models.contract import Contract
from models.contract_photo import ContractPhoto
from models.room_option import RoomOption
from models.like import Like

class ContractForm(FlaskForm):
    pass  # CSRF 토큰을 자동으로 처리

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 기본 필드 추가
        self.fields = {
            'house_name': StringField('건물명', validators=[Optional()]),
            'location': StringField('위치', validators=[DataRequired()]),
            'latitude': FloatField('위도', validators=[DataRequired()]),
            'longitude': FloatField('경도', validators=[DataRequired()]),
            'room_count': IntegerField('방 개수', validators=[DataRequired()]),
            'bathroom_count': FloatField('화장실 개수', validators=[DataRequired()]),
            'roommate_allowed': BooleanField('룸메이트 허용'),
            'start_date': DateField('계약 시작일', format='%Y-%m-%d', validators=[Optional()]),
            'end_date': DateField('계약 종료일', format='%Y-%m-%d', validators=[Optional()]),
            'monthly_rent_usd': FloatField('월세 (달러)', validators=[DataRequired()]),
            'deposit_usd': FloatField('보증금 (달러)', validators=[Optional()]),
            'description': TextAreaField('설명', validators=[Optional()]),
            'seller_kakao': StringField('카카오톡 아이디', validators=[Optional()]),
            'seller_phone': StringField('전화번호', validators=[Optional()]),
            'seller_instagram': StringField('인스타그램 아이디', validators=[Optional()])
        }

contract_bp = Blueprint('contract', __name__, url_prefix='/contract')

# 허용된 이미지 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """파일 확장자 검증"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contract_bp.route('/create', methods=['GET'])
@login_required
def create():
    """매물 등록 페이지"""
    # Google Maps API 키 가져오기
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('contract/create.html', google_maps_api_key=google_maps_api_key)

@contract_bp.route('/create/step1', methods=['POST'])
@login_required
def create_step1():
    """매물 등록 1단계: 기본 정보"""
    if request.headers.get('HX-Request'):
        # HTMX 요청인 경우 다음 단계 폼 반환
        data = {
            'house_name': request.form.get('house_name', ''),
            'location': request.form.get('location', ''),
            'latitude': request.form.get('latitude', ''),
            'longitude': request.form.get('longitude', ''),
            'monthly_rent_usd': request.form.get('monthly_rent_usd', ''),
            'deposit_usd': request.form.get('deposit_usd', ''),
            'transaction_type': request.form.get('transaction_type', ''),
            'seller_kakao': request.form.get('seller_kakao', ''),
            'seller_phone': request.form.get('seller_phone', ''),
            'seller_instagram': request.form.get('seller_instagram', '')
        }
        return render_template('contract/create_step2.html', data=data)
    return redirect(url_for('contract.create'))

@contract_bp.route('/create/step2', methods=['POST'])
@login_required
def create_step2():
    """매물 등록 2단계: 상세 정보"""
    if request.headers.get('HX-Request'):
        # 이전 단계 데이터와 현재 데이터 병합
        data = {
            'house_name': request.form.get('house_name', ''),
            'location': request.form.get('location', ''),
            'latitude': request.form.get('latitude', ''),
            'longitude': request.form.get('longitude', ''),
            'monthly_rent_usd': request.form.get('monthly_rent_usd', ''),
            'deposit_usd': request.form.get('deposit_usd', ''),
            'transaction_type': request.form.get('transaction_type', ''),
            'room_count': request.form.get('room_count', ''),
            'bathroom_count': request.form.get('bathroom_count', ''),
            'build_year': request.form.get('build_year', ''),
            'roommate_allowed': 'roommate_allowed' in request.form,
            'size_sqft': request.form.get('size_sqft', ''),
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'seller_kakao': request.form.get('seller_kakao', ''),
            'seller_phone': request.form.get('seller_phone', ''),
            'seller_instagram': request.form.get('seller_instagram', '')
        }
        return render_template('contract/create_step3.html', data=data)
    return redirect(url_for('contract.create'))

@contract_bp.route('/create/step3', methods=['POST'])
@login_required
def create_step3():
    """매물 등록 3단계: 옵션 및 최종 확인"""
    if request.headers.get('HX-Request'):
        # 이전 단계 데이터와 현재 데이터 병합
        data = {
            'house_name': request.form.get('house_name', ''),
            'location': request.form.get('location', ''),
            'latitude': request.form.get('latitude', ''),
            'longitude': request.form.get('longitude', ''),
            'monthly_rent_usd': request.form.get('monthly_rent_usd', ''),
            'deposit_usd': request.form.get('deposit_usd', ''),
            'transaction_type': request.form.get('transaction_type', ''),
            'room_count': request.form.get('room_count', ''),
            'bathroom_count': request.form.get('bathroom_count', ''),
            'build_year': request.form.get('build_year', ''),
            'roommate_allowed': 'roommate_allowed' in request.form,
            'size_sqft': request.form.get('size_sqft', ''),
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'options': request.form.getlist('options'),
        }
        return render_template('contract/create_final.html', data=data)
    return redirect(url_for('contract.create'))

@contract_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    """매물 등록 최종 제출"""
    try:
        # 폼 데이터에서 계약 정보 추출
        house_name = request.form.get('house_name')
        location = request.form.get('location')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        monthly_rent_usd = float(request.form.get('monthly_rent_usd')) if request.form.get('monthly_rent_usd') else None
        deposit_usd = float(request.form.get('deposit_usd')) if request.form.get('deposit_usd') else None
        room_count = int(request.form.get('room_count')) if request.form.get('room_count') else None
        bathroom_count = float(request.form.get('bathroom_count')) if request.form.get('bathroom_count') else None
        build_year = int(request.form.get('build_year')) if request.form.get('build_year') else None
        roommate_allowed = 'roommate_allowed' in request.form
        size_sqft = float(request.form.get('size_sqft')) if request.form.get('size_sqft') else None
        
        # 판매자 정보
        seller_kakao = request.form.get('seller_kakao', '')
        seller_instagram = request.form.get('seller_instagram', '')
        seller_phone = request.form.get('seller_phone', '')
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        options = request.form.getlist('options')
        description = request.form.get('description', '')
        
        # 새 계약 객체 생성
        new_contract = Contract(
            house_name=house_name,
            location=location,
            monthly_rent_usd=monthly_rent_usd,
            deposit_usd=deposit_usd,
            room_count=room_count,
            bathroom_count=bathroom_count,
            build_year=build_year,
            roommate_allowed=roommate_allowed,
            size_sqft=size_sqft,
            start_date=start_date,
            end_date=end_date,
            description=description,
            posted_by=current_user.id,
            contract_status='active',
            seller_kakao=seller_kakao,
            seller_instagram=seller_instagram,
            seller_phone=seller_phone
        )
        
        db.session.add(new_contract)
        db.session.flush()  # ID 생성을 위한 플러시
        
        # 옵션 추가
        for option in options:
            option_obj = RoomOption(
                contract_id=new_contract.id,
                option_name=option
            )
            db.session.add(option_obj)
        
        # 파일 업로드 처리
        uploaded_files = request.files.getlist('photos')
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        
        # 업로드 디렉토리가 없으면 생성
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                # 파일명 안전하게 변경
                filename = secure_filename(file.filename)
                # UUID를 사용하여 고유한 파일명 생성
                unique_filename = f"{str(uuid.uuid4())}_{filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # 파일 저장
                file.save(file_path)
                
                # 데이터베이스에 파일 정보 저장
                photo = ContractPhoto(
                    file_id=unique_filename,
                    contract_id=new_contract.id
                )
                db.session.add(photo)
        
        db.session.commit()
        flash('매물이 성공적으로 등록되었습니다.', 'success')
        
        # HTMX 요청인 경우 성공 메시지 반환
        if request.headers.get('HX-Request'):
            return render_template('contract/success.html', contract_id=new_contract.id)
        
        return redirect(url_for('main.index'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매물 등록 오류: {e}")
        flash('매물 등록 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
        
        # HTMX 요청인 경우 오류 메시지 반환
        if request.headers.get('HX-Request'):
            return render_template('contract/error.html', error=str(e))
        
        return redirect(url_for('contract.create'))

@contract_bp.route('/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    """사진 업로드 처리 (AJAX)"""
    if 'photo' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{str(uuid.uuid4())}_{filename}"
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'url': url_for('static', filename=f'uploads/{unique_filename}')
            })
        
        except Exception as e:
            current_app.logger.error(f"사진 업로드 오류: {e}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': '허용되지 않는 파일 형식입니다.'}), 400


@contract_bp.route('/search', methods=['GET'])
def search():
    """매물 검색 페이지"""
    # Google Maps API 키 가져오기
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    
    # 검색 쿼리 파라미터
    query = request.args.get('q', '')
    transaction_type = request.args.get('transaction_type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rooms = request.args.get('min_rooms', type=int)
    max_rooms = request.args.get('max_rooms', type=int)
    sort_by = request.args.get('sort_by', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 페이지당 항목 수
    
    # HTMX 요청인 경우 부분 템플릿만 반환
    is_htmx_request = request.headers.get('HX-Request') == 'true'
    
    # 초기 검색이 아닌 경우 (HTMX 요청 또는 파라미터가 있는 경우)
    contracts_query = search_contracts(query, transaction_type, min_price, max_price, min_rooms, max_rooms, sort_by)
    
    # 페이지네이션 적용
    pagination = contracts_query.paginate(page=page, per_page=per_page)
    contracts = pagination.items
    
    if is_htmx_request:
        return render_template(
            'contract/partials/search_results.html',
            contracts=contracts,
            pagination=pagination,
            query=query,
            transaction_type=transaction_type,
            min_price=min_price,
            max_price=max_price,
            min_rooms=min_rooms,
            max_rooms=max_rooms,
            sort_by=sort_by
        )
    
    return render_template(
        'contract/search.html',
        contracts=contracts,
        pagination=pagination,
        google_maps_api_key=google_maps_api_key,
        query=query,
        transaction_type=transaction_type,
        min_price=min_price,
        max_price=max_price,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
        sort_by=sort_by
    )


@contract_bp.route('/search/map', methods=['GET'])
def search_map():
    """지도 기반 매물 검색 API"""
    """지도 기반 매물 검색 API"""
    # 위치 범위 파라미터
    north = request.args.get('north', type=float)
    south = request.args.get('south', type=float)
    east = request.args.get('east', type=float)
    west = request.args.get('west', type=float)
    
    if not all([north, south, east, west]):
        return jsonify({'error': '위치 범위가 올바르지 않습니다.'}), 400
    
    # 추가 필터링 파라미터
    transaction_type = request.args.get('transaction_type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # 계약 쿼리
    query = Contract.query.filter(
        Contract.contract_status == 'active',
        Contract.is_deleted == False
    )
    
    # 위치 필터링
    query = query.filter(
        Contract.latitude <= north,
        Contract.latitude >= south,
        Contract.longitude <= east,
        Contract.longitude >= west
    )
    
    # 거래 유형 필터링
    if transaction_type:
        query = query.filter(Contract.transaction_type == transaction_type)
    
    # 가격 필터링
    if min_price is not None:
        query = query.filter(Contract.monthly_rent_usd >= min_price)
    if max_price is not None:
        query = query.filter(Contract.monthly_rent_usd <= max_price)
    
    # 최대 100개까지만 반환
    contracts = query.limit(100).all()
    
    # 응답 데이터 구성
    result = []
    for contract in contracts:
        result.append({
            'id': contract.id,
            'house_name': contract.house_name,
            'location': contract.location,
            'latitude': float(contract.latitude) if contract.latitude else None,
            'longitude': float(contract.longitude) if contract.longitude else None,
            'monthly_rent_usd': float(contract.monthly_rent_usd) if contract.monthly_rent_usd else None,
            
            'room_count': contract.room_count
        })
    
    return jsonify(result)


@contract_bp.route('/detail/<int:contract_id>', methods=['GET'])
def detail(contract_id):
    """매물 상세 페이지"""
    contract = Contract.query.get_or_404(contract_id)
    
    # 비공개 매물이거나 삭제된 매물인 경우 404 에러
    if contract.is_deleted or contract.contract_status != 'active':
        abort(404)
    
    # 조회수 증가
    contract.view_count += 1
    db.session.commit()
    
    # 매물 사진
    photos = ContractPhoto.query.filter_by(contract_id=contract.id).all()
    
    # 매물 옵션
    options = RoomOption.query.filter_by(contract_id=contract.id).all()
    
    # 작성자 정보 가져오기
    poster = contract.poster
    
    # 로그인 상태에 따라 관심 여부 확인
    is_liked = False
    if current_user.is_authenticated:
        like = Like.query.filter_by(user_id=current_user.id, contract_id=contract.id).first()
        is_liked = like is not None
    
    # 유사한 매물 추천 (동일 지역, 비슷한 가격대)
    similar_contracts = Contract.query.filter(
        Contract.id != contract.id,
        Contract.contract_status == 'active',
        Contract.is_deleted == False,
        Contract.location.like(f'%{contract.location.split()[0]}%')  # 같은 지역(시/군)의 매물
    ).order_by(
        func.abs(Contract.monthly_rent_usd - contract.monthly_rent_usd)  # 가격이 비슷한 순서
    ).limit(4).all()
    
    # 유사 매물 사진
    similar_photos = {}
    for similar in similar_contracts:
        photo = ContractPhoto.query.filter_by(contract_id=similar.id).first()
        if photo:
            similar_photos[similar.id] = photo.file_id
    
    # 작성자 여부 확인
    is_owner = current_user.is_authenticated and contract.posted_by == current_user.id
    
    return render_template('contract/detail.html',
                           contract=contract,
                           photos=photos,
                           options=options,
                           is_liked=is_liked,
                           similar_contracts=similar_contracts,
                           similar_photos=similar_photos,
                           poster=poster,
                           is_owner=is_owner)


@contract_bp.route('/like/<int:contract_id>', methods=['POST'])
@login_required
def toggle_like(contract_id):
    """매물 관심 등록/해제"""
    contract = Contract.query.get_or_404(contract_id)
    
    # 이미 관심 등록되어 있는지 확인
    existing_like = Like.query.filter_by(user_id=current_user.id, contract_id=contract.id).first()
    
    if existing_like:
        # 관심 해제
        db.session.delete(existing_like)
        is_liked = False
        message = '관심 매물에서 제거되었습니다.'
    else:
        # 관심 등록
        new_like = Like(user_id=current_user.id, contract_id=contract.id)
        db.session.add(new_like)
        is_liked = True
        message = '관심 매물로 등록되었습니다.'
    
    db.session.commit()
    
    # HTMX 요청인 경우 부분적인 응답 반환
    if request.headers.get('HX-Request') == 'true':
        return render_template('contract/partials/like_button.html', 
                               contract_id=contract.id, 
                               is_liked=is_liked)
    
    # 일반 요청인 경우 JSON 응답 반환
    return jsonify({
        'success': True,
        'is_liked': is_liked,
        'message': message
    })

@contract_bp.route('/delete/<int:contract_id>', methods=['GET'])
@login_required
def confirm_delete(contract_id):
    """매물 삭제 확인 페이지"""
    contract = Contract.query.get_or_404(contract_id)
    
    # 작성자만 접근 가능
    if contract.posted_by != current_user.id:
        abort(403)
    
    form = ContractForm()
    return render_template('contract/delete.html', contract=contract, form=form)

@contract_bp.route('/delete/<int:contract_id>/confirm', methods=['POST'])
@login_required
def delete_contract(contract_id):
    """매물 삭제 처리"""
    contract = Contract.query.get_or_404(contract_id)
    
    # 작성자만 삭제 가능
    if contract.posted_by != current_user.id:
        abort(403)
    
    form = ContractForm()
    if form.validate_on_submit():
        # 매물 상태를 비활성화로 변경
        contract.contract_status = 'cancelled'
        contract.is_deleted = True
        
        # 관련 데이터 삭제
        ContractPhoto.query.filter_by(contract_id=contract.id).delete()
        RoomOption.query.filter_by(contract_id=contract.id).delete()
        Like.query.filter_by(contract_id=contract.id).delete()
        
        db.session.commit()
        
        flash('매물이 삭제되었습니다.', 'success')
        return redirect(url_for('main.index'))

@contract_bp.route('/edit/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    """매물 수정"""
    contract = Contract.query.get_or_404(contract_id)
    
    # 작성자만 수정 가능
    if contract.posted_by != current_user.id:
        abort(403)
    
    # 매물 옵션 가져오기
    options = RoomOption.query.filter_by(contract_id=contract.id).all()
    selected_options = [option.option_name for option in options]
    
    form = ContractForm()
    if form.validate_on_submit():
        # 기본 정보 업데이트
        contract.house_name = request.form.get('house_name')
        contract.location = request.form.get('location')
        contract.latitude = request.form.get('latitude')
        contract.longitude = request.form.get('longitude')
        
        # 숫자 필드 처리
        def safe_convert(value, converter):
            if not value:
                return None
            try:
                return converter(value)
            except ValueError:
                return None
        
        contract.monthly_rent_usd = safe_convert(request.form.get('monthly_rent_usd'), float)
        contract.deposit_usd = safe_convert(request.form.get('deposit_usd'), float)
        contract.room_count = safe_convert(request.form.get('room_count'), int)
        contract.bathroom_count = safe_convert(request.form.get('bathroom_count'), float)
        contract.build_year = safe_convert(request.form.get('build_year'), int)
        contract.size_sqft = safe_convert(request.form.get('size_sqft'), float)
        
        contract.roommate_allowed = 'roommate_allowed' in request.form
        
        # 날짜 업데이트
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        contract.start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        contract.end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # 설명 업데이트
        contract.description = request.form.get('description')
        
        # 옵션 업데이트
        existing_options = RoomOption.query.filter_by(contract_id=contract.id).all()
        for option in existing_options:
            db.session.delete(option)
        
        new_options = request.form.getlist('options')
        for option in new_options:
            new_option = RoomOption(
                contract_id=contract.id,
                option_name=option
            )
            db.session.add(new_option)
        
        # 수정 정보 업데이트
        contract.modified_by = current_user.id
        contract.modified_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('매물이 수정되었습니다.', 'success')
        return redirect(url_for('contract.detail', contract_id=contract.id))
        # 기본 정보 업데이트
        contract.house_name = request.form.get('house_name')
        contract.location = request.form.get('location')
        contract.latitude = request.form.get('latitude')
        contract.longitude = request.form.get('longitude')
        contract.monthly_rent_usd = float(request.form.get('monthly_rent_usd'))
        contract.deposit_usd = float(request.form.get('deposit_usd')) if request.form.get('deposit_usd') else None
        contract.room_count = int(request.form.get('room_count'))
        contract.bathroom_count = float(request.form.get('bathroom_count'))
        contract.build_year = int(request.form.get('build_year'))
        contract.roommate_allowed = 'roommate_allowed' in request.form
        contract.size_sqft = float(request.form.get('size_sqft'))
        
        # 날짜 업데이트
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        contract.start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        contract.end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # 설명 업데이트
        contract.description = request.form.get('description')
        
        # 옵션 업데이트
        existing_options = RoomOption.query.filter_by(contract_id=contract.id).all()
        for option in existing_options:
            db.session.delete(option)
        
        new_options = request.form.getlist('options')
        for option in new_options:
            new_option = RoomOption(
                contract_id=contract.id,
                option_name=option
            )
            db.session.add(new_option)
        
        # 수정 정보 업데이트
        contract.modified_by = current_user.id
        contract.modified_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('매물이 수정되었습니다.', 'success')
        return redirect(url_for('contract.detail', contract_id=contract.id))
    
     # GET 요청 시, edit.html 렌더링
    # form 객체는 이미 함수 상단에서 form = ContractForm()으로 생성되어 사용 가능합니다.
    # edit.html은 contract 객체의 속성을 직접 사용하므로, 별도의 data 딕셔너리는 필요 없습니다.
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('contract/edit.html',
                         form=form,
                         contract=contract,
                         selected_options=selected_options,
                         google_maps_api_key=google_maps_api_key)


def search_contracts(query='', transaction_type='', min_price=None, max_price=None, min_rooms=None, max_rooms=None, sort_by='newest'):
    """매물 검색 함수"""
    # 기본 쿼리: 활성 상태이고 삭제되지 않은 매물
    contracts_query = Contract.query.filter(
        Contract.contract_status == 'active',
        Contract.is_deleted == False
    )
    
    # 텍스트 검색
    if query:
        search_terms = [f'%{term}%' for term in query.split()]
        search_conditions = []
        
        for term in search_terms:
            search_conditions.append(or_(
                Contract.house_name.ilike(term),
                Contract.location.ilike(term)
            ))
        
        contracts_query = contracts_query.filter(and_(*search_conditions))
    
    # 거래 유형 필터링
    if transaction_type:
        contracts_query = contracts_query.filter(Contract.transaction_type == transaction_type)
    
    # 가격 범위 필터링
    if min_price is not None:
        contracts_query = contracts_query.filter(Contract.monthly_rent_usd >= min_price)
    if max_price is not None:
        contracts_query = contracts_query.filter(Contract.monthly_rent_usd <= max_price)
    
    # 방 개수 필터링
    if min_rooms is not None:
        contracts_query = contracts_query.filter(Contract.room_count >= min_rooms)
    if max_rooms is not None:
        contracts_query = contracts_query.filter(Contract.room_count <= max_rooms)
    
    # 정렬
    if sort_by == 'price_low':
        contracts_query = contracts_query.order_by(Contract.monthly_rent_usd.asc())
    elif sort_by == 'price_high':
        contracts_query = contracts_query.order_by(Contract.monthly_rent_usd.desc())
    elif sort_by == 'popular':
        contracts_query = contracts_query.order_by(Contract.view_count.desc())
    else:  # 'newest' (기본값)
        contracts_query = contracts_query.order_by(Contract.posted_at.desc())
    
    return contracts_query
