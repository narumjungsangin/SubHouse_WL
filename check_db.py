import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 계약 테이블의 모든 레코드 조회
cursor.execute("SELECT id, seller_kakao, seller_instagram, seller_phone FROM contracts")
rows = cursor.fetchall()

print("Contracts in database:")
for row in rows:
    print(f"Contract ID: {row[0]}")
    print(f"Seller Kakao: {row[1]}")
    print(f"Seller Instagram: {row[2]}")
    print(f"Seller Phone: {row[3]}")
    print("-" * 50)

# 연결 종료
conn.close()
