from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
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
    house_name = StringField('건물명', validators=[Optional()])
    location = StringField('위치', validators=[DataRequired()])
    latitude = FloatField('위도', validators=[Optional()])
    longitude = FloatField('경도', validators=[Optional()])
    room_count = IntegerField('방 개수', validators=[DataRequired()])
    bathroom_count = FloatField('화장실 개수', validators=[DataRequired()])
    roommate_allowed = BooleanField('룸메이트 허용')
    start_date = DateField('계약 시작일', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('계약 종료일', format='%Y-%m-%d', validators=[Optional()])
    monthly_rent_usd = FloatField('월세 (달러)', validators=[DataRequired()])
    deposit_usd = FloatField('보증금 (달러)', validators=[Optional()])
    description = TextAreaField('설명', validators=[Optional()])
    seller_kakao = StringField('카카오톡 아이디', validators=[Optional()])
    seller_phone = StringField('전화번호', validators=[Optional()])
    seller_instagram = StringField('인스타그램 아이디', validators=[Optional()])
    photos = MultipleFileField('사진 업로드', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 업로드 가능합니다!')
    ])
    # CSRF 토큰은 FlaskForm에서 자동으로 처리됩니다.

    # __init__ 메소드는 특별한 로직이 없다면 생략 가능합니다.
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

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
            'floor': request.form.get('floor', ''),
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
        # 파일 업로드 처리
        uploaded_files = request.files.getlist('photos')
        temp_upload_dir = os.path.join(current_app.static_folder, 'uploads', 'temp')
        
        if not os.path.exists(temp_upload_dir):
            os.makedirs(temp_upload_dir)

        temp_filenames = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{str(uuid.uuid4())}_{filename}"
                file_path = os.path.join(temp_upload_dir, unique_filename)
                file.save(file_path)
                temp_filenames.append(unique_filename)

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
            'floor': request.form.get('floor', ''),
            'roommate_allowed': request.form.get('roommate_allowed') == 'True',
            'size_sqft': request.form.get('size_sqft', ''),
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'options': request.form.getlist('options'),
            'photos': temp_filenames
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
        
        latitude_str = request.form.get('latitude')
        longitude_str = request.form.get('longitude')
        latitude = float(latitude_str) if latitude_str and latitude_str not in ('', 'undefined') else None
        longitude = float(longitude_str) if longitude_str and longitude_str not in ('', 'undefined') else None
        monthly_rent_usd = float(request.form.get('monthly_rent_usd')) if request.form.get('monthly_rent_usd') else None
        deposit_usd = float(request.form.get('deposit_usd')) if request.form.get('deposit_usd') else None
        room_count = int(request.form.get('room_count')) if request.form.get('room_count') else None
        bathroom_count = float(request.form.get('bathroom_count')) if request.form.get('bathroom_count') else None
        floor = request.form.get('floor') if request.form.get('floor') else None
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
            latitude=latitude,
            longitude=longitude,
            monthly_rent_usd=monthly_rent_usd,
            deposit_usd=deposit_usd,
            room_count=room_count,
            bathroom_count=bathroom_count,
            floor=floor,
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
        
        # 임시 업로드된 사진 처리
        temp_filenames = request.form.getlist('photos')
        temp_dir = os.path.join(current_app.static_folder, 'uploads', 'temp')
        upload_dir = os.path.join(current_app.static_folder, 'uploads')

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for filename in temp_filenames:
            temp_path = os.path.join(temp_dir, filename)
            final_path = os.path.join(upload_dir, filename)
            
            if os.path.exists(temp_path):
                # 임시 파일을 최종 위치로 이동
                os.rename(temp_path, final_path)
                
                # DB에 사진 정보 저장 (상대 경로 사용)
                relative_path = os.path.join(os.path.basename(current_app.config['UPLOAD_FOLDER']), filename).replace('\\', '/')
                current_app.logger.debug(f"[Submit] Saving photo with relative_path: {relative_path}") # 디버깅 로그 추가
                new_photo = ContractPhoto(
                    file_id=filename,
                    file_path=relative_path,
                    contract_id=new_contract.id
                )
                db.session.add(new_photo)
        
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

    # 각 매물의 대표 사진 조회
    contract_photos = {}
    for contract in contracts:
        photo = ContractPhoto.query.filter_by(contract_id=contract.id).first()
        if photo:
            contract_photos[contract.id] = photo.file_id
    
    if is_htmx_request:
        return render_template(
            'contract/partials/search_results.html',
            contracts=contracts,
            pagination=pagination,
            contract_photos=contract_photos,
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
        contract_photos=contract_photos,
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
    
    # 관리자 이메일 (실제 환경에서는 설정 파일 등에서 관리하는 것이 좋습니다)
    ADMIN_EMAIL = 'joonst26@gmail.com'
    is_admin = current_user.is_authenticated and current_user.email == ADMIN_EMAIL

    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('contract/detail.html',
                           contract=contract,
                           photos=photos,
                           options=options,
                           is_liked=is_liked,
                           similar_contracts=similar_contracts,
                           similar_photos=similar_photos,
                           poster=poster,
                           is_owner=is_owner,
                           is_admin=is_admin,
                           google_maps_api_key=google_maps_api_key)


@contract_bp.route('/edit/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    """매물 수정"""
    contract = Contract.query.get_or_404(contract_id)

    if contract.posted_by != current_user.id and not current_user.is_admin:
        abort(403)

    # POST 요청 시에는 제출된 데이터로 폼을 생성하고, GET 요청 시에는 DB 데이터로 폼을 채웁니다.
    # 이렇게 하면 파일 필드의 유효성 검사 오류를 방지할 수 있습니다.
    if request.method == 'POST':
        form = ContractForm()
    else:
        form = ContractForm(obj=contract)

    if form.validate_on_submit():
        # populate_obj는 모든 필드를 덮어쓰므로, 필요한 필드만 수동으로 업데이트합니다.
        contract.house_name = form.house_name.data
        contract.location = form.location.data
        contract.latitude = form.latitude.data
        contract.longitude = form.longitude.data
        contract.room_count = form.room_count.data
        contract.bathroom_count = form.bathroom_count.data
        contract.roommate_allowed = form.roommate_allowed.data
        contract.start_date = form.start_date.data
        contract.end_date = form.end_date.data
        contract.monthly_rent_usd = form.monthly_rent_usd.data
        contract.deposit_usd = form.deposit_usd.data
        contract.description = form.description.data
        contract.seller_kakao = form.seller_kakao.data
        contract.seller_phone = form.seller_phone.data
        contract.seller_instagram = form.seller_instagram.data
        contract.updated_at = datetime.utcnow()

        # 옵션 정보 업데이트
        RoomOption.query.filter_by(contract_id=contract.id).delete()
        selected_options = request.form.getlist('options')
        for option_name in selected_options:
            option = RoomOption(contract_id=contract.id, option_name=option_name)
            db.session.add(option)

        # 사진 업로드 처리 (form.photos.data 사용)
        if form.photos.data:
            for photo_file in form.photos.data:
                if photo_file and allowed_file(photo_file.filename):
                    filename = secure_filename(photo_file.filename)
                    unique_id = str(uuid.uuid4())
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{unique_id}.{file_ext}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                        
                    file_path = os.path.join(upload_folder, unique_filename)
                    photo_file.save(file_path)
                    
                    relative_path = os.path.join(os.path.basename(current_app.config['UPLOAD_FOLDER']), unique_filename).replace('\\', '/')
                    current_app.logger.debug(f"[Edit] Saving photo with relative_path: {relative_path}") # 디버깅 로그 추가
                    new_photo = ContractPhoto(
                        contract_id=contract.id,
                        file_id=unique_filename,
                        file_path=relative_path
                    )
                    db.session.add(new_photo)

        try:
            db.session.commit()
            flash('매물 정보가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('contract.detail', contract_id=contract.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating contract {contract.id}: {e}")
            flash('매물 정보 수정 중 오류가 발생했습니다.', 'danger')

    if form.errors:
        current_app.logger.warning(f"Contract edit form validation failed. Errors: {form.errors}")

    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    option_names = ['furnished', 'parking', 'laundry', 'ac', 'wifi', 'kitchen', 'elevator', 'pets_allowed']
    current_options = {opt.option_name for opt in contract.room_options}
    
    return render_template('contract/edit.html', 
                           form=form, 
                           contract=contract, 
                           google_maps_api_key=google_maps_api_key,
                           option_names=option_names,
                           current_options=current_options)

@contract_bp.route('/delete_photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """사진 삭제 처리 (AJAX/HTMX)"""
    photo = ContractPhoto.query.get_or_404(photo_id)
    contract = Contract.query.get_or_404(photo.contract_id)

    if contract.posted_by != current_user.id and not current_user.is_admin:
        abort(403)

    try:
        # UPLOAD_FOLDER 경로와 photo.file_id를 결합하여 전체 파일 경로를 만듭니다.
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.file_id)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(photo)
        db.session.commit()
        
        # HTMX 요청에 대해 빈 응답을 보내 해당 HTML 요소를 제거하도록 함
        return '', 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting photo {photo_id}: {e}")
        return jsonify({'success': False, 'message': '사진 삭제 중 오류가 발생했습니다.'}), 500


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

    # 작성자 또는 관리자만 삭제 가능
    if contract.posted_by != current_user.id and not current_user.is_admin:
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
