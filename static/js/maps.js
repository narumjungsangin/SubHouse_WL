// Google Maps 관련 기능

let map;
let marker;
let autocomplete;

// 지도 초기화 함수
function initMap() {
    let initialLat = 40.4259; // 기본 위도 (West Lafayette)
    let initialLng = -86.9081; // 기본 경도 (West Lafayette)
    let initialZoom = 13; // 기본 확대 수준

    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');

    // 위도와 경도 input이 존재하고 값이 있는 경우 (수정 페이지)
    if (latInput && lngInput && latInput.value && lngInput.value) {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);
        // 유효한 숫자인지 확인
        if (!isNaN(lat) && !isNaN(lng)) {
            initialLat = lat;
            initialLng = lng;
            initialZoom = 15; // 기존 매물은 더 확대해서 보여줌
        }
    }

    const initialPosition = { lat: initialLat, lng: initialLng };

    map = new google.maps.Map(document.getElementById('map'), {
        center: initialPosition,
        zoom: initialZoom,
        mapTypeControl: false,
        streetViewControl: false
    });

    marker = new google.maps.Marker({
        position: initialPosition,
        map: map,
        draggable: true
    });

    // 마커 드래그 이벤트
    google.maps.event.addListener(marker, 'dragend', function() {
        const position = marker.getPosition();
        document.getElementById('latitude').value = position.lat();
        document.getElementById('longitude').value = position.lng();
        
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: position }, function(results, status) {
            if (status === 'OK' && results[0]) {
                document.getElementById('location').value = results[0].formatted_address;
            }
        });
    });
    
    // 주소 자동완성
    const input = document.getElementById('location');
    if (input) {
        autocomplete = new google.maps.places.Autocomplete(input);
        autocomplete.setFields(['address_components', 'geometry', 'name']);
        
        autocomplete.addListener('place_changed', function() {
            const place = autocomplete.getPlace();
            
            if (!place.geometry) {
                return;
            }
            
            map.setCenter(place.geometry.location);
            marker.setPosition(place.geometry.location);
            
            document.getElementById('latitude').value = place.geometry.location.lat();
            document.getElementById('longitude').value = place.geometry.location.lng();
        });
    }
    
    // 지도 클릭 이벤트
    google.maps.event.addListener(map, 'click', function(event) {
        marker.setPosition(event.latLng);
        document.getElementById('latitude').value = event.latLng.lat();
        document.getElementById('longitude').value = event.latLng.lng();
        
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: event.latLng }, function(results, status) {
            if (status === 'OK' && results[0]) {
                document.getElementById('location').value = results[0].formatted_address;
            }
        });
    });
}

// 특정 좌표로 지도 이동
function moveToLocation(lat, lng) {
    const latLng = new google.maps.LatLng(lat, lng);
    map.setCenter(latLng);
    marker.setPosition(latLng);
}

// 주소로 지도 이동
function geocodeAddress(address) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, function(results, status) {
        if (status === 'OK' && results[0]) {
            map.setCenter(results[0].geometry.location);
            marker.setPosition(results[0].geometry.location);
            
            document.getElementById('latitude').value = results[0].geometry.location.lat();
            document.getElementById('longitude').value = results[0].geometry.location.lng();
        }
    });
}
