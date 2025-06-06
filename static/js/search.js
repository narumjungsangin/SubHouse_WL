// 전역 변수
let map;
let markers = [];
let mapVisible = false;
let lastBounds = null;

// Google Maps 초기화
function initMap() {
    // 기본 위치 (서울 중심)
    const defaultLocation = { lat: 37.5665, lng: 126.9780 };
    
    // 지도 초기화
    map = new google.maps.Map(document.getElementById('map-container'), {
        center: defaultLocation,
        zoom: 13,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    // 지도 움직임 이벤트 처리
    map.addListener('idle', () => {
        if (mapVisible) {
            const bounds = map.getBounds();
            
            // 지도 경계가 크게 변경된 경우에만 새로운 데이터 요청
            if (!lastBounds || boundsChangedSignificantly(bounds, lastBounds)) {
                fetchPropertiesInView(bounds);
                lastBounds = bounds;
            }
        }
    });
    
    // 주소 자동완성
    const input = document.getElementById('q');
    if (input) {
        const autocomplete = new google.maps.places.Autocomplete(input);
        
        autocomplete.addListener('place_changed', () => {
            const place = autocomplete.getPlace();
            
            if (place.geometry && place.geometry.location) {
                // 검색창에 선택된 위치로 지도 이동 (지도가 보이는 경우)
                if (mapVisible) {
                    map.setCenter(place.geometry.location);
                    map.setZoom(15);
                }
            }
        });
    }
}

// 지도 경계가 유의미하게 변경되었는지 확인
function boundsChangedSignificantly(newBounds, oldBounds) {
    if (!oldBounds) return true;
    
    const oldNE = oldBounds.getNorthEast();
    const oldSW = oldBounds.getSouthWest();
    const newNE = newBounds.getNorthEast();
    const newSW = newBounds.getSouthWest();
    
    // 경계의 25% 이상 변경 시 유의미한 변경으로 간주
    const latChange = Math.abs(oldNE.lat() - newNE.lat()) > Math.abs(oldNE.lat() - oldSW.lat()) * 0.25 ||
                     Math.abs(oldSW.lat() - newSW.lat()) > Math.abs(oldNE.lat() - oldSW.lat()) * 0.25;
    
    const lngChange = Math.abs(oldNE.lng() - newNE.lng()) > Math.abs(oldNE.lng() - oldSW.lng()) * 0.25 ||
                     Math.abs(oldSW.lng() - newSW.lng()) > Math.abs(oldNE.lng() - oldSW.lng()) * 0.25;
    
    return latChange || lngChange;
}

// 현재 보이는 지도 영역의 매물 정보 가져오기
function fetchPropertiesInView(bounds) {
    // 현재 마커 제거
    clearMarkers();
    
    // 현재 필터 값 가져오기
    const transactionType = document.getElementById('transaction_type')?.value || '';
    const minPrice = document.getElementById('min_price')?.value || '';
    const maxPrice = document.getElementById('max_price')?.value || '';
    
    // API 요청 URL 생성
    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();
    
    let url = `/contract/search/map?north=${ne.lat()}&south=${sw.lat()}&east=${ne.lng()}&west=${sw.lng()}`;
    
    // 필터 추가
    if (transactionType) url += `&transaction_type=${transactionType}`;
    if (minPrice) url += `&min_price=${minPrice}`;
    if (maxPrice) url += `&max_price=${maxPrice}`;
    
    // API 요청
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // 마커 생성
            data.forEach(property => {
                if (property.latitude && property.longitude) {
                    addMarker(property);
                }
            });
        })
        .catch(error => {
            console.error('매물 데이터를 가져오는 중 오류 발생:', error);
        });
}

// 마커 추가
function addMarker(property) {
    const marker = new google.maps.Marker({
        position: { lat: property.latitude, lng: property.longitude },
        map: map,
        title: property.house_name
    });
    
    // 마커 클릭 시 정보창 표시
    marker.addListener('click', () => {
        // 상세 페이지로 이동
        window.location.href = `/contract/detail/${property.id}`;
    });
    
    // 마커에 호버 시 매물 정보 표시
    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div style="width: 200px;">
                <h3 style="font-weight: bold; margin-bottom: 5px;">${property.house_name}</h3>
                <p style="margin-bottom: 5px;">${property.location}</p>
                <p style="color: #2563EB; font-weight: bold;">$${Math.round(property.monthly_rent_usd)}</p>
                <p>방 ${property.room_count}개</p>
                <a href="/contract/detail/${property.id}" style="color: #2563EB; display: block; margin-top: 5px;">상세 보기</a>
            </div>
        `
    });
    
    marker.addListener('mouseover', () => {
        infoWindow.open(map, marker);
    });
    
    marker.addListener('mouseout', () => {
        infoWindow.close();
    });
    
    // 전역 마커 배열에 추가
    markers.push(marker);
}

// 모든 마커 제거
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

// 지도 토글 버튼 이벤트 처리
document.addEventListener('DOMContentLoaded', () => {
    const showMapButton = document.getElementById('show-map');
    const closeMapButton = document.getElementById('close-map');
    const mapSearch = document.getElementById('map-search');
    
    if (showMapButton && closeMapButton && mapSearch) {
        showMapButton.addEventListener('click', () => {
            mapSearch.classList.remove('hidden');
            mapVisible = true;
            
            // 지도 리사이즈 (화면에 표시된 후 호출 필요)
            setTimeout(() => {
                google.maps.event.trigger(map, 'resize');
                
                // 현재 보이는 영역의 매물 가져오기
                const bounds = map.getBounds();
                if (bounds) {
                    fetchPropertiesInView(bounds);
                    lastBounds = bounds;
                }
            }, 100);
        });
        
        closeMapButton.addEventListener('click', () => {
            mapSearch.classList.add('hidden');
            mapVisible = false;
        });
    }
    
    // 필터 초기화 시 지도 마커도 초기화
    const resetButton = document.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', () => {
            if (mapVisible && map.getBounds()) {
                setTimeout(() => {
                    fetchPropertiesInView(map.getBounds());
                }, 100);
            }
        });
    }
    
    // 필터 변경 시 지도 마커도 업데이트
    const filterInputs = [
        document.getElementById('transaction_type'),
        document.getElementById('min_price'),
        document.getElementById('max_price')
    ];
    
    filterInputs.forEach(input => {
        if (input) {
            input.addEventListener('change', () => {
                if (mapVisible && map.getBounds()) {
                    fetchPropertiesInView(map.getBounds());
                }
            });
        }
    });
});
