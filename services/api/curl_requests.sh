#!/bin/bash

# FastAPI Housing Price Predictor - Curl Requests
# Uruchom: chmod +x curl_requests.sh && ./curl_requests.sh

BASE_URL="http://localhost:8000"

echo "🚀 Testowanie FastAPI Housing Price Predictor"
echo "=============================================="

# 1. Test głównego endpointu
echo ""
echo "1️⃣ Test głównego endpointu:"
curl -X GET "$BASE_URL/" \
  -H "accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 2. Predykcja ceny mieszkania - 50m², 2 pokoje
echo ""
echo "2️⃣ Predykcja ceny mieszkania (50m², 2 pokoje):"
curl -X POST "$BASE_URL/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "area_m2": 50.0,
    "rooms": 2
  }' \
  -w "\nStatus: %{http_code}\n"

# 3. Predykcja ceny mieszkania - 70m², 3 pokoje
echo ""
echo "3️⃣ Predykcja ceny mieszkania (70m², 3 pokoje):"
curl -X POST "$BASE_URL/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "area_m2": 70.0,
    "rooms": 3
  }' \
  -w "\nStatus: %{http_code}\n"

# 4. Predykcja ceny mieszkania - 30m², 1 pokój
echo ""
echo "4️⃣ Predykcja ceny mieszkania (30m², 1 pokój):"
curl -X POST "$BASE_URL/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "area_m2": 30.0,
    "rooms": 1
  }' \
  -w "\nStatus: %{http_code}\n"

# 5. Dodanie nowej oferty
echo ""
echo "5️⃣ Dodanie nowej oferty:"
curl -X POST "$BASE_URL/offers/" \
  -H "Content-Type: application/json" \
  -d '{
    "locality": "Wrocław Śródmieście",
    "rooms": 3,
    "area_m2": 65.0
  }' \
  -w "\nStatus: %{http_code}\n"

# 6. Dodanie kolejnej oferty
echo ""
echo "6️⃣ Dodanie kolejnej oferty:"
curl -X POST "$BASE_URL/offers/" \
  -H "Content-Type: application/json" \
  -d '{
    "locality": "Wrocław Krzyki",
    "rooms": 2,
    "area_m2": 45.0
  }' \
  -w "\nStatus: %{http_code}\n"

# 7. Pobranie wszystkich ofert
echo ""
echo "7️⃣ Pobranie wszystkich ofert:"
curl -X GET "$BASE_URL/offers/" \
  -H "accept: application/json" \
  -w "\nStatus: %{http_code}\n"

# 8. Statystyki dzielnicy
echo ""
echo "8️⃣ Statystyki dzielnicy:"
curl -X GET "$BASE_URL/offers/stats?locality=Wrocław%20Krzyki" \
  -H "accept: application/json" \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "✅ Testy zakończone!"
echo ""
echo "📖 Dokumentacja API dostępna pod:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
