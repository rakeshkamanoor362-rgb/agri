from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime
import json
import uuid
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'agrolink-secret-2024'

# ---- In-memory database ----
users_db = {
    "farmer1": {"password": "pass123", "role": "farmer", "name": "Ramesh Kumar", "location": "Punjab", "avatar": "🧑‍🌾", "verified": True, "rating": 4.8},
    "buyer1":  {"password": "pass123", "role": "buyer",  "name": "Priya Exports", "location": "Delhi",  "avatar": "🏪", "verified": True, "rating": 4.6},
    "owner1":  {"password": "pass123", "role": "equipment_owner", "name": "Singh Tractors", "location": "Haryana", "avatar": "🚜", "verified": True, "rating": 4.9},
    "transport1": {"password": "pass123", "role": "transport", "name": "FastCrop Logistics", "location": "UP", "avatar": "🚛", "verified": True, "rating": 4.7},
    "admin":   {"password": "admin123", "role": "admin", "name": "AgroLink Admin", "location": "HQ", "avatar": "⚙️", "verified": True, "rating": 5.0},
}

equipment_db = [
    {"id":"eq1","name":"John Deere 5050D Tractor","category":"tractor","price":1200,"unit":"day","location":"Ludhiana, Punjab","owner":"owner1","owner_name":"Singh Tractors","rating":4.9,"reviews":42,"image":"🚜","available":True,"hp":50,"year":2022,"description":"Well-maintained tractor ideal for wheat & paddy fields. AC cabin available.","lat":30.9010,"lng":75.8573},
    {"id":"eq2","name":"CLAAS Lexion Harvester","category":"harvester","price":3500,"unit":"day","location":"Karnal, Haryana","owner":"owner1","owner_name":"Singh Tractors","rating":4.7,"reviews":28,"image":"🌾","available":True,"hp":320,"year":2021,"description":"High-capacity combine harvester. Covers 15 acres/day.","lat":29.6857,"lng":76.9905},
    {"id":"eq3","name":"Rotavator 7ft","category":"rotavator","price":800,"unit":"day","location":"Amritsar, Punjab","owner":"farmer1","owner_name":"Ramesh Kumar","rating":4.5,"reviews":15,"image":"⚙️","available":True,"hp":0,"year":2023,"description":"Heavy-duty rotavator for soil preparation.","lat":31.6340,"lng":74.8723},
    {"id":"eq4","name":"Agricultural Drone DJI Agras","category":"drone","price":2000,"unit":"day","location":"Hisar, Haryana","owner":"owner1","owner_name":"Singh Tractors","rating":4.8,"reviews":33,"image":"🛸","available":True,"hp":0,"year":2023,"description":"Precision spraying drone covers 40 acres/day. GPS guided.","lat":29.1492,"lng":75.7217},
    {"id":"eq5","name":"Paddy Seeder 8-row","category":"seeder","price":600,"unit":"day","location":"Patiala, Punjab","owner":"farmer1","owner_name":"Ramesh Kumar","rating":4.6,"reviews":19,"image":"🌱","available":False,"hp":0,"year":2022,"description":"8-row paddy seeder with depth control.","lat":30.3398,"lng":76.3869},
    {"id":"eq6","name":"Potato Digger Machine","category":"other","price":950,"unit":"day","location":"Agra, UP","owner":"owner1","owner_name":"Singh Tractors","rating":4.4,"reviews":11,"image":"🥔","available":True,"hp":65,"year":2020,"description":"Efficient potato harvesting machine.","lat":27.1767,"lng":78.0081},
]

crops_db = [
    {"id":"cr1","name":"Premium Basmati Rice","category":"grains","price":45,"unit":"kg","quantity":5000,"location":"Karnal, Haryana","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.8,"freshness":"Fresh","harvest_date":"2024-11-20","image":"🌾","description":"Grade-A basmati rice, long grain, fragrant. Direct from farm.","emergency":False,"lat":29.6857,"lng":76.9905,"verified":True},
    {"id":"cr2","name":"Organic Tomatoes","category":"vegetables","price":25,"unit":"kg","quantity":800,"location":"Nashik, Maharashtra","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.6,"freshness":"Fresh","harvest_date":"2024-11-22","image":"🍅","description":"Pesticide-free organic tomatoes. Harvested 2 days ago.","emergency":True,"lat":20.0059,"lng":73.7912,"verified":True},
    {"id":"cr3","name":"Yellow Mustard Seeds","category":"oilseeds","price":58,"unit":"kg","quantity":3000,"location":"Bharatpur, Rajasthan","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.7,"freshness":"Dried","harvest_date":"2024-11-10","image":"🌻","description":"High oil content mustard seeds. Ideal for oil extraction.","emergency":False,"lat":27.2152,"lng":77.4892,"verified":True},
    {"id":"cr4","name":"Fresh Spinach","category":"vegetables","price":18,"unit":"kg","quantity":200,"location":"Delhi NCR","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.5,"freshness":"Very Fresh","harvest_date":"2024-11-23","image":"🥬","description":"Morning harvest spinach. Must sell within 2 days.","emergency":True,"lat":28.6139,"lng":77.2090,"verified":False},
    {"id":"cr5","name":"Alphonso Mangoes","category":"fruits","price":180,"unit":"kg","quantity":500,"location":"Ratnagiri, Maharashtra","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.9,"freshness":"Fresh","harvest_date":"2024-11-21","image":"🥭","description":"GI-tagged Alphonso mangoes. Export quality available.","emergency":False,"lat":16.9902,"lng":73.3120,"verified":True},
    {"id":"cr6","name":"Raw Cotton Bales","category":"fiber","price":65,"unit":"kg","quantity":10000,"location":"Vidarbha, Maharashtra","farmer":"farmer1","farmer_name":"Ramesh Kumar","rating":4.3,"freshness":"Dried","harvest_date":"2024-11-15","image":"☁️","description":"Long-staple cotton. Gin-ready bales.","emergency":False,"lat":20.7002,"lng":77.0082,"verified":True},
]

posts_db = [
    {"id":"p1","author":"farmer1","author_name":"Ramesh Kumar","avatar":"🧑‍🌾","title":"Best practices for wheat sowing in November","content":"I've been farming wheat for 20 years in Punjab. Here are my tips for getting maximum yield this rabi season: 1) Soil pH between 6.5-7.5 is ideal 2) Use certified HD-2967 variety seeds 3) First irrigation at crown root initiation stage...","likes":47,"comments":[{"author":"Priya Exports","text":"Very helpful! We noticed better grain quality from farmers following these practices.","time":"2h ago"},{"author":"Singh Tractors","text":"Also recommend rotavator preparation 2 weeks before sowing for better tilth.","time":"1h ago"}],"tags":["wheat","rabi","Punjab"],"time":"5h ago","lang":"en"},
    {"id":"p2","author":"farmer1","author_name":"Suresh Patel","avatar":"🌾","title":"Drone spraying vs manual - my experience","content":"Tried drone spraying this kharif season on my 15-acre cotton field. Results were surprising. 40% reduction in pesticide use, uniform coverage, and saved 3 days of labor costs. ROI was positive in just one season...","likes":89,"comments":[{"author":"Singh Tractors","text":"We offer DJI Agras T40 for rent at ₹2000/day. Covers 40 acres easily.","time":"3h ago"}],"tags":["drone","cotton","technology"],"time":"1d ago","lang":"en"},
    {"id":"p3","author":"farmer1","author_name":"Gurpreet Singh","avatar":"👨‍🌾","title":"MSP for paddy - should we demand increase?","content":"MSP at ₹2183/quintal doesn't cover our input costs anymore. Fertilizer prices up 40%, diesel up 30%. We need MSP of at least ₹2600. What do other farmers think?","likes":234,"comments":[{"author":"Ramesh Kumar","text":"Absolutely agree. Input costs have risen much faster than MSP.","time":"30m ago"}],"tags":["MSP","policy","paddy"],"time":"2d ago","lang":"en"},
]

transport_db = [
    {"id":"tr1","name":"FastCrop Logistics","type":"refrigerated","capacity":"10 tons","price":2500,"unit":"trip","location":"Delhi Hub","owner":"transport1","rating":4.8,"reviews":67,"available":True,"image":"🚛","description":"Temperature-controlled trucks for perishables. GPS tracked."},
    {"id":"tr2","name":"KisanTransport Pro","type":"flatbed","capacity":"20 tons","price":1800,"unit":"trip","location":"Punjab Hub","owner":"transport1","rating":4.6,"reviews":43,"available":True,"image":"🚐","description":"Bulk grain transport. Tarpaulin covered."},
    {"id":"tr3","name":"SpeedyHarvest Movers","type":"mini-truck","capacity":"2 tons","price":800,"unit":"trip","location":"Local - 50km radius","owner":"transport1","rating":4.5,"reviews":28,"available":False,"image":"🚚","description":"Small farm to market delivery. Same day."},
]

labor_db = [
    {"id":"lb1","name":"Rajendra & Team","skills":["harvesting","planting","irrigation"],"workers":8,"daily_rate":450,"location":"Muzaffarpur, Bihar","rating":4.7,"reviews":34,"available":True,"image":"👷","description":"Experienced team. Available for seasonal work across India."},
    {"id":"lb2","name":"Punjab Farm Workers","skills":["wheat harvesting","paddy transplanting","tractor operation"],"workers":15,"daily_rate":500,"location":"Jalandhar, Punjab","rating":4.8,"reviews":52,"available":True,"image":"🌾","description":"Skilled paddy and wheat workers. Bring own tools."},
    {"id":"lb3","name":"Mango Harvest Specialists","skills":["fruit picking","grading","packing"],"workers":6,"daily_rate":550,"location":"Ratnagiri, Maharashtra","rating":4.9,"reviews":29,"available":True,"image":"🥭","description":"Expert fruit harvesters. Handle with care certified."},
]

messages_db = {}  # room_id -> list of messages

bookings_db = []

# ---- HTML TEMPLATE ----
HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AgroLink – Connecting Agriculture</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
:root {
  --green-900: #14532d;
  --green-800: #166534;
  --green-700: #15803d;
  --green-600: #16a34a;
  --green-500: #22c55e;
  --green-400: #4ade80;
  --green-300: #86efac;
  --green-100: #dcfce7;
  --green-50:  #f0fdf4;
  --earth-900: #431407;
  --earth-800: #7c2d12;
  --earth-600: #c2410c;
  --earth-400: #fb923c;
  --earth-200: #fed7aa;
  --earth-50:  #fff7ed;
  --gold:      #f59e0b;
  --gold-light:#fef3c7;
  --bg:        #f8faf7;
  --bg2:       #ffffff;
  --bg3:       #f0fdf4;
  --text:      #111827;
  --text2:     #374151;
  --text3:     #6b7280;
  --border:    #d1fae5;
  --shadow:    0 4px 24px rgba(22,163,74,0.10);
  --shadow-lg: 0 8px 40px rgba(22,163,74,0.18);
  --radius:    16px;
  --radius-sm: 10px;
  --header-h: 68px;
}
[data-theme="dark"] {
  --bg:     #0d1f12;
  --bg2:    #132a1a;
  --bg3:    #1a3622;
  --text:   #f0fdf4;
  --text2:  #bbf7d0;
  --text3:  #86efac;
  --border: #166534;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
}
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;transition:background .3s,color .3s;}

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--green-400);border-radius:99px;}

/* ---- LAYOUT ---- */
.app-container{display:flex;flex-direction:column;min-height:100vh;}
.page{display:none;animation:fadeIn .4s ease;}
.page.active{display:block;}
@keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

/* ---- HEADER ---- */
header{position:sticky;top:0;z-index:100;background:var(--bg2);border-bottom:2px solid var(--border);height:var(--header-h);display:flex;align-items:center;padding:0 20px;gap:12px;box-shadow:var(--shadow);}
.logo{display:flex;align-items:center;gap:10px;cursor:pointer;text-decoration:none;}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,var(--green-600),var(--green-800));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(22,163,74,.3);}
.logo-text{font-family:'Syne',sans-serif;font-weight:800;font-size:22px;background:linear-gradient(135deg,var(--green-700),var(--green-500));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.logo-sub{font-size:10px;color:var(--text3);font-weight:500;margin-top:-4px;letter-spacing:.5px;}
nav{display:flex;gap:4px;margin-left:auto;flex-wrap:wrap;}
.nav-btn{background:none;border:none;padding:8px 14px;border-radius:var(--radius-sm);cursor:pointer;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;color:var(--text2);transition:all .2s;white-space:nowrap;}
.nav-btn:hover,.nav-btn.active{background:var(--green-100);color:var(--green-700);}
[data-theme="dark"] .nav-btn:hover,[data-theme="dark"] .nav-btn.active{background:var(--green-900);color:var(--green-400);}
.header-actions{display:flex;align-items:center;gap:8px;margin-left:12px;}
.icon-btn{width:38px;height:38px;border-radius:10px;border:1.5px solid var(--border);background:var(--bg3);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s;color:var(--text2);font-size:15px;}
.icon-btn:hover{background:var(--green-100);border-color:var(--green-400);color:var(--green-700);}
.notif-badge{position:relative;}
.notif-badge .badge{position:absolute;top:-4px;right:-4px;width:16px;height:16px;background:var(--earth-600);border-radius:50%;font-size:9px;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;}
.user-pill{display:flex;align-items:center;gap:8px;background:var(--bg3);border:1.5px solid var(--border);border-radius:99px;padding:5px 14px 5px 6px;cursor:pointer;transition:all .2s;}
.user-pill:hover{border-color:var(--green-400);}
.user-avatar{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--green-500),var(--green-700));display:flex;align-items:center;justify-content:center;font-size:14px;}
.user-name{font-size:13px;font-weight:600;color:var(--text);}

/* ---- HERO ---- */
.hero{min-height:calc(100vh - var(--header-h));background:linear-gradient(160deg,var(--green-50) 0%,#fff 40%,var(--earth-50) 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;text-align:center;position:relative;overflow:hidden;}
[data-theme="dark"] .hero{background:linear-gradient(160deg,var(--green-900) 0%,var(--bg) 50%,#1a0e06 100%);}
.hero-bg-pattern{position:absolute;inset:0;opacity:.04;background-image:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2316a34a' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:var(--green-100);border:1.5px solid var(--green-300);border-radius:99px;padding:6px 16px;font-size:13px;font-weight:600;color:var(--green-800);margin-bottom:24px;animation:slideDown .6s ease;}
[data-theme="dark"] .hero-badge{background:var(--green-900);border-color:var(--green-700);color:var(--green-300);}
@keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:none}}
.hero-title{font-family:'Syne',sans-serif;font-size:clamp(36px,7vw,72px);font-weight:800;line-height:1.05;margin-bottom:20px;animation:heroTitle .8s ease .1s both;}
@keyframes heroTitle{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
.hero-title .accent{background:linear-gradient(135deg,var(--green-600),var(--green-400));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-title .accent2{background:linear-gradient(135deg,var(--earth-600),var(--gold));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{font-size:clamp(16px,2.5vw,20px);color:var(--text2);max-width:600px;line-height:1.6;margin-bottom:36px;animation:heroTitle .8s ease .2s both;}
.hero-actions{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;animation:heroTitle .8s ease .3s both;}
.btn-primary{background:linear-gradient(135deg,var(--green-600),var(--green-700));color:#fff;border:none;padding:14px 28px;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;transition:all .25s;box-shadow:0 4px 16px rgba(22,163,74,.35);font-family:'DM Sans',sans-serif;}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(22,163,74,.45);}
.btn-secondary{background:var(--bg2);color:var(--green-700);border:2px solid var(--green-400);padding:14px 28px;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;transition:all .25s;font-family:'DM Sans',sans-serif;}
.btn-secondary:hover{background:var(--green-50);transform:translateY(-2px);}
.hero-stats{display:flex;gap:32px;margin-top:56px;flex-wrap:wrap;justify-content:center;animation:heroTitle .8s ease .5s both;}
.stat{text-align:center;}
.stat-num{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:var(--green-700);}
.stat-label{font-size:12px;color:var(--text3);font-weight:500;margin-top:2px;}
.hero-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;max-width:900px;width:100%;margin-top:48px;animation:heroTitle .8s ease .4s both;}
.hero-card{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px 16px;cursor:pointer;transition:all .3s;text-align:center;}
.hero-card:hover{transform:translateY(-6px);border-color:var(--green-400);box-shadow:var(--shadow-lg);}
.hero-card .hc-icon{font-size:32px;margin-bottom:10px;}
.hero-card .hc-title{font-size:14px;font-weight:700;color:var(--text);font-family:'Syne',sans-serif;}
.hero-card .hc-sub{font-size:11px;color:var(--text3);margin-top:4px;}

/* ---- SECTIONS ---- */
.section{padding:32px 20px;max-width:1200px;margin:0 auto;width:100%;}
.section-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:12px;}
.section-title{font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:var(--text);}
.section-sub{font-size:14px;color:var(--text3);margin-top:2px;}
.see-all{color:var(--green-600);font-size:14px;font-weight:600;cursor:pointer;text-decoration:none;display:flex;align-items:center;gap:4px;}
.see-all:hover{color:var(--green-800);}

/* ---- SEARCH BAR ---- */
.search-bar{display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap;}
.search-input-wrap{flex:1;min-width:200px;position:relative;}
.search-input-wrap i{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--text3);font-size:14px;}
.search-input{width:100%;padding:12px 16px 12px 40px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:var(--bg2);color:var(--text);font-size:14px;font-family:'DM Sans',sans-serif;transition:all .2s;}
.search-input:focus{outline:none;border-color:var(--green-400);box-shadow:0 0 0 3px rgba(74,222,128,.15);}
.filter-select{padding:12px 16px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:var(--bg2);color:var(--text);font-size:14px;cursor:pointer;font-family:'DM Sans',sans-serif;}
.filter-select:focus{outline:none;border-color:var(--green-400);}

/* ---- CARDS GRID ---- */
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;}
.card{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);overflow:hidden;transition:all .3s;cursor:pointer;}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg);border-color:var(--green-300);}
.card-img{height:140px;background:linear-gradient(135deg,var(--green-100),var(--green-50));display:flex;align-items:center;justify-content:center;font-size:56px;position:relative;}
[data-theme="dark"] .card-img{background:linear-gradient(135deg,var(--green-900),var(--bg3));}
.card-badge{position:absolute;top:10px;right:10px;padding:4px 10px;border-radius:99px;font-size:11px;font-weight:700;}
.badge-available{background:var(--green-100);color:var(--green-700);}
.badge-unavailable{background:#fee2e2;color:#b91c1c;}
.badge-emergency{background:#fef08a;color:#92400e;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
.badge-fresh{background:var(--green-100);color:var(--green-700);}
.card-body{padding:16px;}
.card-title{font-family:'Syne',sans-serif;font-weight:700;font-size:16px;margin-bottom:6px;color:var(--text);}
.card-meta{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text3);margin-bottom:10px;flex-wrap:wrap;}
.card-meta i{font-size:11px;}
.card-price{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:var(--green-700);}
.card-price span{font-size:12px;font-weight:400;color:var(--text3);}
.card-footer{display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding-top:12px;border-top:1px solid var(--border);}
.rating{display:flex;align-items:center;gap:4px;font-size:13px;font-weight:600;color:var(--gold);}
.btn-sm{padding:8px 16px;border-radius:var(--radius-sm);font-size:13px;font-weight:600;border:none;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;}
.btn-green{background:var(--green-600);color:#fff;}
.btn-green:hover{background:var(--green-700);transform:scale(1.03);}
.btn-outline{background:none;border:1.5px solid var(--green-400);color:var(--green-700);}
.btn-outline:hover{background:var(--green-50);}
.btn-orange{background:var(--earth-600);color:#fff;}
.btn-orange:hover{background:var(--earth-800);}

/* ---- EMERGENCY SECTION ---- */
.emergency-banner{background:linear-gradient(135deg,#7c2d12,#c2410c);border-radius:var(--radius);padding:20px 24px;margin-bottom:28px;display:flex;align-items:center;gap:16px;color:#fff;}
.emergency-banner i{font-size:28px;animation:shake .5s infinite;}
@keyframes shake{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
.emergency-banner .eb-text h3{font-family:'Syne',sans-serif;font-size:18px;font-weight:800;}
.emergency-banner .eb-text p{font-size:13px;opacity:.85;margin-top:4px;}

/* ---- WEATHER WIDGET ---- */
.weather-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:28px;}
.weather-card{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center;}
.weather-card .wc-icon{font-size:40px;margin-bottom:8px;}
.weather-card .wc-temp{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:var(--green-700);}
.weather-card .wc-city{font-size:14px;font-weight:600;color:var(--text);}
.weather-card .wc-desc{font-size:12px;color:var(--text3);margin-top:4px;}
.weather-details{display:flex;justify-content:center;gap:16px;margin-top:12px;font-size:12px;color:var(--text3);}
.mandi-table{width:100%;border-collapse:collapse;font-size:14px;}
.mandi-table th{background:var(--green-700);color:#fff;padding:10px 14px;text-align:left;font-weight:600;}
.mandi-table td{padding:10px 14px;border-bottom:1px solid var(--border);}
.mandi-table tr:hover td{background:var(--green-50);}
[data-theme="dark"] .mandi-table tr:hover td{background:var(--green-900);}
.price-up{color:#16a34a;font-weight:600;}
.price-down{color:#dc2626;font-weight:600;}

/* ---- FORUM ---- */
.forum-post{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:16px;transition:all .2s;}
.forum-post:hover{border-color:var(--green-300);}
.fp-header{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
.fp-avatar{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--green-500),var(--green-700));display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}
.fp-meta{flex:1;}
.fp-author{font-weight:700;font-size:15px;color:var(--text);}
.fp-time{font-size:12px;color:var(--text3);}
.fp-title{font-family:'Syne',sans-serif;font-size:17px;font-weight:700;margin-bottom:10px;color:var(--text);}
.fp-content{font-size:14px;color:var(--text2);line-height:1.6;margin-bottom:14px;}
.fp-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;}
.fp-tag{background:var(--green-100);color:var(--green-800);padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;}
[data-theme="dark"] .fp-tag{background:var(--green-900);color:var(--green-300);}
.fp-actions{display:flex;gap:12px;align-items:center;}
.fp-action{background:none;border:none;color:var(--text3);font-size:13px;cursor:pointer;display:flex;align-items:center;gap:5px;padding:6px 10px;border-radius:var(--radius-sm);transition:all .2s;font-family:'DM Sans',sans-serif;}
.fp-action:hover{background:var(--green-50);color:var(--green-700);}
[data-theme="dark"] .fp-action:hover{background:var(--green-900);color:var(--green-400);}
.fp-action.liked{color:var(--earth-600);}
.fp-comments{border-top:1px solid var(--border);margin-top:14px;padding-top:14px;display:none;}
.fp-comment{display:flex;gap:10px;margin-bottom:12px;}
.fc-avatar{width:30px;height:30px;border-radius:50%;background:var(--green-100);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;}
.fc-body{background:var(--bg3);border-radius:var(--radius-sm);padding:10px 14px;flex:1;}
.fc-author{font-size:12px;font-weight:700;color:var(--green-700);margin-bottom:4px;}
.fc-text{font-size:13px;color:var(--text2);}
.new-post-btn{display:flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--green-600),var(--green-700));color:#fff;border:none;padding:12px 24px;border-radius:var(--radius-sm);font-size:14px;font-weight:600;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;}
.new-post-btn:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(22,163,74,.35);}

/* ---- CHAT ---- */
.chat-layout{display:grid;grid-template-columns:280px 1fr;gap:0;background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);overflow:hidden;height:600px;}
.chat-sidebar{border-right:1.5px solid var(--border);overflow-y:auto;}
.chat-sidebar-header{padding:16px;border-bottom:1px solid var(--border);font-family:'Syne',sans-serif;font-weight:700;font-size:15px;display:flex;align-items:center;gap:8px;}
.chat-item{padding:14px 16px;cursor:pointer;transition:all .2s;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;}
.chat-item:hover,.chat-item.active{background:var(--green-50);}
[data-theme="dark"] .chat-item:hover,[data-theme="dark"] .chat-item.active{background:var(--green-900);}
.ci-avatar{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--green-500),var(--green-700));display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.ci-info{flex:1;min-width:0;}
.ci-name{font-size:14px;font-weight:600;color:var(--text);}
.ci-preview{font-size:12px;color:var(--text3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ci-meta{display:flex;flex-direction:column;align-items:flex-end;gap:4px;}
.ci-time{font-size:11px;color:var(--text3);}
.ci-unread{background:var(--green-600);color:#fff;border-radius:99px;font-size:10px;font-weight:700;padding:2px 7px;}
.chat-main{display:flex;flex-direction:column;}
.chat-main-header{padding:16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;}
.chat-messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;}
.msg{max-width:70%;display:flex;flex-direction:column;gap:3px;}
.msg.sent{align-self:flex-end;align-items:flex-end;}
.msg.recv{align-self:flex-start;align-items:flex-start;}
.msg-bubble{padding:10px 14px;border-radius:18px;font-size:14px;line-height:1.5;}
.msg.sent .msg-bubble{background:var(--green-600);color:#fff;border-bottom-right-radius:4px;}
.msg.recv .msg-bubble{background:var(--bg3);color:var(--text);border-bottom-left-radius:4px;border:1px solid var(--border);}
.msg-time{font-size:10px;color:var(--text3);}
.chat-input-area{padding:14px 16px;border-top:1px solid var(--border);display:flex;gap:10px;align-items:flex-end;}
.chat-input{flex:1;border:1.5px solid var(--border);border-radius:12px;padding:10px 14px;font-size:14px;background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;resize:none;outline:none;transition:border .2s;min-height:42px;max-height:120px;}
.chat-input:focus{border-color:var(--green-400);}
.chat-send-btn{width:42px;height:42px;background:var(--green-600);border:none;border-radius:12px;color:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0;}
.chat-send-btn:hover{background:var(--green-700);transform:scale(1.05);}

/* ---- AUTH MODAL ---- */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:1000;display:none;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px);}
.modal-overlay.open{display:flex;}
.modal{background:var(--bg2);border-radius:20px;padding:32px;width:100%;max-width:440px;position:relative;animation:modalIn .3s ease;}
@keyframes modalIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:none}}
.modal-close{position:absolute;top:16px;right:16px;background:var(--bg3);border:none;width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;color:var(--text2);}
.modal-title{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;margin-bottom:6px;}
.modal-sub{font-size:13px;color:var(--text3);margin-bottom:24px;}
.form-group{margin-bottom:16px;}
.form-label{font-size:13px;font-weight:600;color:var(--text2);margin-bottom:6px;display:block;}
.form-input{width:100%;padding:12px 14px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:14px;background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;transition:all .2s;}
.form-input:focus{outline:none;border-color:var(--green-400);box-shadow:0 0 0 3px rgba(74,222,128,.1);}
.role-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px;}
.role-option{border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:12px;cursor:pointer;transition:all .2s;text-align:center;}
.role-option:hover,.role-option.selected{border-color:var(--green-400);background:var(--green-50);}
[data-theme="dark"] .role-option:hover,[data-theme="dark"] .role-option.selected{background:var(--green-900);}
.role-option .ro-icon{font-size:24px;margin-bottom:4px;}
.role-option .ro-text{font-size:12px;font-weight:600;color:var(--text);}
.auth-toggle{text-align:center;margin-top:16px;font-size:13px;color:var(--text3);}
.auth-toggle a{color:var(--green-600);font-weight:600;cursor:pointer;}
.demo-accounts{background:var(--green-50);border:1px solid var(--green-200);border-radius:var(--radius-sm);padding:12px;margin-bottom:16px;font-size:12px;}
[data-theme="dark"] .demo-accounts{background:var(--green-900);border-color:var(--green-800);}
.demo-accounts h4{font-weight:700;color:var(--green-700);margin-bottom:8px;}
.demo-accounts p{color:var(--text3);line-height:1.8;}

/* ---- DASHBOARD ---- */
.dashboard-header{background:linear-gradient(135deg,var(--green-700),var(--green-900));color:#fff;padding:28px 24px;border-radius:var(--radius);margin-bottom:24px;}
.dh-greeting{font-size:14px;opacity:.8;margin-bottom:4px;}
.dh-name{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;margin-bottom:8px;}
.dh-role{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.15);border-radius:99px;padding:4px 14px;font-size:12px;font-weight:600;}
.dash-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:24px;}
.dash-stat{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center;}
.ds-icon{font-size:28px;margin-bottom:8px;}
.ds-num{font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:var(--green-700);}
.ds-label{font-size:12px;color:var(--text3);margin-top:4px;}
.dash-tabs{display:flex;gap:4px;margin-bottom:24px;background:var(--bg3);border-radius:var(--radius-sm);padding:4px;flex-wrap:wrap;}
.dash-tab{flex:1;min-width:100px;background:none;border:none;padding:10px 16px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500;color:var(--text2);transition:all .2s;font-family:'DM Sans',sans-serif;}
.dash-tab.active{background:var(--bg2);color:var(--green-700);font-weight:600;box-shadow:var(--shadow);}
.dash-content{display:none;}
.dash-content.active{display:block;}

/* ---- TOAST ---- */
.toast-container{position:fixed;bottom:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:8px;}
.toast{background:var(--bg2);border-left:4px solid var(--green-500);border-radius:var(--radius-sm);padding:14px 18px;box-shadow:var(--shadow-lg);font-size:14px;min-width:280px;animation:toastIn .3s ease;display:flex;align-items:center;gap:10px;}
.toast.error{border-left-color:#ef4444;}
.toast.warning{border-left-color:var(--gold);}
@keyframes toastIn{from{opacity:0;transform:translateX(100%)}to{opacity:1;transform:none}}
@keyframes toastOut{to{opacity:0;transform:translateX(100%)}}

/* ---- NOTIF PANEL ---- */
.notif-panel{position:fixed;top:var(--header-h);right:0;width:360px;max-height:calc(100vh - var(--header-h));background:var(--bg2);border-left:1.5px solid var(--border);box-shadow:-4px 0 24px rgba(0,0,0,.1);z-index:90;overflow-y:auto;transform:translateX(100%);transition:transform .3s;padding-bottom:20px;}
.notif-panel.open{transform:none;}
.notif-panel-header{padding:20px 20px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;font-family:'Syne',sans-serif;font-weight:700;position:sticky;top:0;background:var(--bg2);}
.notif-item{padding:14px 20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .2s;}
.notif-item:hover{background:var(--green-50);}
[data-theme="dark"] .notif-item:hover{background:var(--green-900);}
.notif-item.unread{background:var(--green-50);}
[data-theme="dark"] .notif-item.unread{background:rgba(22,163,74,.08);}
.ni-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px;}
.ni-sub{font-size:12px;color:var(--text3);}
.ni-time{font-size:11px;color:var(--text3);margin-top:4px;}

/* ---- ADMIN ---- */
.admin-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px;}
.admin-card{background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;display:flex;align-items:center;gap:16px;}
.ac-icon{width:52px;height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}
.ac-icon.green{background:var(--green-100);color:var(--green-700);}
.ac-icon.orange{background:var(--earth-200);color:var(--earth-600);}
.ac-icon.blue{background:#dbeafe;color:#1d4ed8;}
.ac-icon.purple{background:#ede9fe;color:#7c3aed;}
.ac-num{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:var(--text);}
.ac-label{font-size:12px;color:var(--text3);}

/* ---- BOOKING MODAL ---- */
.booking-form{padding:0;}
.bk-summary{background:var(--green-50);border-radius:var(--radius-sm);padding:14px;margin-bottom:20px;}
[data-theme="dark"] .bk-summary{background:var(--green-900);}
.bk-item-name{font-weight:700;font-size:16px;color:var(--green-700);}
.bk-price{font-size:13px;color:var(--text3);margin-top:4px;}

/* ---- MOBILE NAV ---- */
.mobile-nav{display:none;position:fixed;bottom:0;left:0;right:0;background:var(--bg2);border-top:1.5px solid var(--border);z-index:100;padding:8px 0 calc(8px + env(safe-area-inset-bottom));box-shadow:0 -4px 20px rgba(0,0,0,.1);}
.mn-items{display:flex;justify-content:space-around;align-items:center;}
.mn-item{display:flex;flex-direction:column;align-items:center;gap:3px;cursor:pointer;padding:6px 12px;border-radius:var(--radius-sm);transition:all .2s;border:none;background:none;}
.mn-item i{font-size:18px;color:var(--text3);transition:color .2s;}
.mn-item span{font-size:10px;color:var(--text3);font-weight:500;}
.mn-item.active i,.mn-item.active span{color:var(--green-600);}

/* ---- FOOTER ---- */
footer{background:var(--green-900);color:rgba(255,255,255,.85);padding:48px 20px 24px;margin-top:auto;}
.footer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:32px;max-width:1200px;margin:0 auto;}
.footer-brand .logo-text{-webkit-text-fill-color:var(--green-300);}
.footer-brand p{font-size:13px;margin-top:12px;line-height:1.6;opacity:.75;}
.footer-col h4{font-family:'Syne',sans-serif;font-weight:700;font-size:14px;color:var(--green-300);margin-bottom:14px;}
.footer-col a{display:block;font-size:13px;color:rgba(255,255,255,.65);margin-bottom:8px;cursor:pointer;text-decoration:none;transition:color .2s;}
.footer-col a:hover{color:var(--green-300);}
.footer-bottom{max-width:1200px;margin:32px auto 0;padding-top:24px;border-top:1px solid rgba(255,255,255,.1);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:12px;opacity:.6;}

/* ---- RESPONSIVE ---- */
@media(max-width:768px){
  nav{display:none;}
  .header-actions .user-pill .user-name{display:none;}
  .mobile-nav{display:block;}
  body{padding-bottom:72px;}
  .chat-layout{grid-template-columns:1fr;height:500px;}
  .chat-sidebar{display:none;}
  .hero-stats{gap:20px;}
  .stat-num{font-size:24px;}
  .section{padding:20px 14px;}
}
@media(max-width:480px){
  .cards-grid{grid-template-columns:1fr;}
  .hero-title{font-size:32px;}
  .chat-layout{grid-template-columns:1fr;}
  .chat-sidebar{display:none;}
}
</style>
</head>
<body>

<!-- HEADER -->
<header>
  <a class="logo" onclick="showPage('home')">
    <div class="logo-icon">🌾</div>
    <div>
      <div class="logo-text">AgroLink</div>
      <div class="logo-sub">CONNECTING AGRICULTURE</div>
    </div>
  </a>
  <nav id="mainNav">
    <button class="nav-btn active" onclick="showPage('home')"><i class="fa fa-home"></i> Home</button>
    <button class="nav-btn" onclick="showPage('equipment')"><i class="fa fa-tractor"></i> Equipment</button>
    <button class="nav-btn" onclick="showPage('marketplace')"><i class="fa fa-store"></i> Market</button>
    <button class="nav-btn" onclick="showPage('transport')"><i class="fa fa-truck"></i> Transport</button>
    <button class="nav-btn" onclick="showPage('labor')"><i class="fa fa-users"></i> Labor</button>
    <button class="nav-btn" onclick="showPage('weather')"><i class="fa fa-cloud-sun"></i> Weather</button>
    <button class="nav-btn" onclick="showPage('forum')"><i class="fa fa-comments"></i> Forum</button>
    <button class="nav-btn" onclick="showPage('chat')"><i class="fa fa-message"></i> Chat</button>
  </nav>
  <div class="header-actions">
    <button class="icon-btn" onclick="toggleTheme()" title="Toggle theme"><i class="fa fa-moon" id="themeIcon"></i></button>
    <div class="icon-btn notif-badge" onclick="toggleNotifPanel()">
      <i class="fa fa-bell"></i>
      <span class="badge">3</span>
    </div>
    <div id="userPill" class="user-pill" onclick="handleUserClick()">
      <div class="user-avatar" id="headerAvatar">👤</div>
      <span class="user-name" id="headerName">Login</span>
    </div>
  </div>
</header>

<!-- NOTIFICATION PANEL -->
<div class="notif-panel" id="notifPanel">
  <div class="notif-panel-header">
    <span>🔔 Notifications</span>
    <button onclick="toggleNotifPanel()" style="background:none;border:none;cursor:pointer;font-size:18px;color:var(--text3)">×</button>
  </div>
  <div class="notif-item unread">
    <div class="ni-title">🚜 Booking Confirmed</div>
    <div class="ni-sub">Your John Deere 5050D tractor booking for Dec 1-3 is confirmed by Singh Tractors.</div>
    <div class="ni-time">10 minutes ago</div>
  </div>
  <div class="notif-item unread">
    <div class="ni-title">💰 New Bid on Your Crop</div>
    <div class="ni-sub">Priya Exports placed a bid of ₹48/kg on your Basmati Rice listing.</div>
    <div class="ni-time">1 hour ago</div>
  </div>
  <div class="notif-item unread">
    <div class="ni-title">⚡ Emergency Alert</div>
    <div class="ni-sub">Fresh Spinach near you is available for emergency sale at ₹15/kg. Act fast!</div>
    <div class="ni-time">3 hours ago</div>
  </div>
  <div class="notif-item">
    <div class="ni-title">🌧️ Weather Alert</div>
    <div class="ni-sub">Heavy rain expected in Punjab this weekend. Consider delaying harvest.</div>
    <div class="ni-time">Yesterday</div>
  </div>
  <div class="notif-item">
    <div class="ni-title">⭐ New Review</div>
    <div class="ni-sub">Singh Tractors left you a 5-star review for your last rental.</div>
    <div class="ni-time">2 days ago</div>
  </div>
</div>

<!-- PAGES -->
<div class="app-container">

<!-- HOME PAGE -->
<div class="page active" id="page-home">
  <div class="hero">
    <div class="hero-bg-pattern"></div>
    <div class="hero-badge"><span>🌱</span> India's #1 Agriculture Platform</div>
    <h1 class="hero-title">
      Grow More,<br>
      <span class="accent">Earn More</span><br>
      with <span class="accent2">AgroLink</span>
    </h1>
    <p class="hero-sub">Connect farmers, buyers, equipment owners, transporters and workers on one powerful platform. From field to market, we've got you covered.</p>
    <div class="hero-actions">
      <button class="btn-primary" onclick="openAuth('register')">🚀 Get Started Free</button>
      <button class="btn-secondary" onclick="showPage('marketplace')">🌾 Browse Market</button>
    </div>
    <div class="hero-cards">
      <div class="hero-card" onclick="showPage('equipment')">
        <div class="hc-icon">🚜</div>
        <div class="hc-title">Rent Equipment</div>
        <div class="hc-sub">Tractors, harvesters & more</div>
      </div>
      <div class="hero-card" onclick="showPage('marketplace')">
        <div class="hc-icon">🌾</div>
        <div class="hc-title">Sell Crops</div>
        <div class="hc-sub">Direct to buyers</div>
      </div>
      <div class="hero-card" onclick="showPage('transport')">
        <div class="hc-icon">🚛</div>
        <div class="hc-title">Book Transport</div>
        <div class="hc-sub">Farm to market delivery</div>
      </div>
      <div class="hero-card" onclick="showPage('labor')">
        <div class="hc-icon">👷</div>
        <div class="hc-title">Hire Labor</div>
        <div class="hc-sub">Skilled farm workers</div>
      </div>
      <div class="hero-card" onclick="showPage('weather')">
        <div class="hc-icon">☀️</div>
        <div class="hc-title">Weather & Mandi</div>
        <div class="hc-sub">Live prices & forecasts</div>
      </div>
      <div class="hero-card" onclick="showPage('forum')">
        <div class="hc-icon">💬</div>
        <div class="hc-title">Community</div>
        <div class="hc-sub">Connect with farmers</div>
      </div>
    </div>
    <div class="hero-stats">
      <div class="stat"><div class="stat-num">2.4L+</div><div class="stat-label">Farmers</div></div>
      <div class="stat"><div class="stat-num">18K+</div><div class="stat-label">Equipment Listed</div></div>
      <div class="stat"><div class="stat-num">₹840Cr+</div><div class="stat-label">Transactions</div></div>
      <div class="stat"><div class="stat-num">28</div><div class="stat-label">States Covered</div></div>
    </div>
  </div>
</div>

<!-- EQUIPMENT PAGE -->
<div class="page" id="page-equipment">
  <div class="section">
    <div class="section-header">
      <div>
        <div class="section-title">🚜 Equipment Rental</div>
        <div class="section-sub">Rent tractors, harvesters, drones & more near you</div>
      </div>
      <button class="btn-primary btn-sm" onclick="openListEquipment()">+ List Equipment</button>
    </div>
    <div class="search-bar">
      <div class="search-input-wrap">
        <i class="fa fa-search"></i>
        <input type="text" class="search-input" id="eqSearch" placeholder="Search equipment..." oninput="filterEquipment()">
      </div>
      <select class="filter-select" id="eqCategory" onchange="filterEquipment()">
        <option value="">All Categories</option>
        <option value="tractor">Tractors</option>
        <option value="harvester">Harvesters</option>
        <option value="drone">Drones</option>
        <option value="seeder">Seeders</option>
        <option value="rotavator">Rotavators</option>
        <option value="other">Other</option>
      </select>
      <select class="filter-select" id="eqAvail" onchange="filterEquipment()">
        <option value="">All Status</option>
        <option value="available">Available</option>
        <option value="unavailable">Booked</option>
      </select>
    </div>
    <div class="cards-grid" id="equipmentGrid"></div>
  </div>
</div>

<!-- MARKETPLACE PAGE -->
<div class="page" id="page-marketplace">
  <div class="section">
    <div class="section-header">
      <div>
        <div class="section-title">🌾 Crop Marketplace</div>
        <div class="section-sub">Buy directly from farmers. Fresh from the field.</div>
      </div>
      <button class="btn-primary btn-sm" onclick="openListCrop()">+ List Crop</button>
    </div>

    <!-- Emergency Section -->
    <div class="emergency-banner">
      <i class="fa fa-fire"></i>
      <div class="eb-text">
        <h3>⚡ Emergency Crop Sales</h3>
        <p>Perishable crops that need to be sold urgently. Act fast to avoid wastage!</p>
      </div>
      <button class="btn-sm" style="background:rgba(255,255,255,.2);color:#fff;border:1px solid rgba(255,255,255,.3);margin-left:auto;" onclick="filterCrops('emergency')">View All</button>
    </div>
    <div class="cards-grid" id="emergencyGrid" style="margin-bottom:32px;"></div>

    <div class="section-header">
      <div class="section-title">All Crops</div>
    </div>
    <div class="search-bar">
      <div class="search-input-wrap">
        <i class="fa fa-search"></i>
        <input type="text" class="search-input" id="cropSearch" placeholder="Search crops..." oninput="filterCrops()">
      </div>
      <select class="filter-select" id="cropCategory" onchange="filterCrops()">
        <option value="">All Categories</option>
        <option value="grains">Grains</option>
        <option value="vegetables">Vegetables</option>
        <option value="fruits">Fruits</option>
        <option value="oilseeds">Oilseeds</option>
        <option value="fiber">Fiber</option>
      </select>
    </div>
    <div class="cards-grid" id="cropsGrid"></div>
  </div>
</div>

<!-- TRANSPORT PAGE -->
<div class="page" id="page-transport">
  <div class="section">
    <div class="section-header">
      <div>
        <div class="section-title">🚛 Transport Booking</div>
        <div class="section-sub">Reliable crop delivery across India</div>
      </div>
      <button class="btn-primary btn-sm" onclick="openListTransport()">+ List Vehicle</button>
    </div>
    <div class="cards-grid" id="transportGrid"></div>
  </div>
</div>

<!-- LABOR PAGE -->
<div class="page" id="page-labor">
  <div class="section">
    <div class="section-header">
      <div>
        <div class="section-title">👷 Labor Hiring</div>
        <div class="section-sub">Find skilled agricultural workers for your farm</div>
      </div>
      <button class="btn-primary btn-sm" onclick="openListLabor()">+ List as Worker</button>
    </div>
    <div class="cards-grid" id="laborGrid"></div>
  </div>
</div>

<!-- WEATHER PAGE -->
<div class="page" id="page-weather">
  <div class="section">
    <div class="section-header">
      <div class="section-title">☀️ Weather & Mandi Prices</div>
      <div class="section-sub">Live agricultural market data</div>
    </div>
    <div class="weather-grid" id="weatherGrid"></div>
    <div class="section-header" style="margin-top:32px;">
      <div>
        <div class="section-title">📈 Mandi Market Prices</div>
        <div class="section-sub">Today's rates from major mandis across India</div>
      </div>
      <span style="font-size:12px;color:var(--text3);">Last updated: <span id="mandiTime"></span></span>
    </div>
    <div style="overflow-x:auto;border-radius:var(--radius);border:1.5px solid var(--border);overflow:hidden;">
    <table class="mandi-table" id="mandiTable">
      <thead><tr><th>Crop</th><th>Mandi</th><th>Price (₹/Qtl)</th><th>Change</th><th>MSP</th></tr></thead>
      <tbody></tbody>
    </table>
    </div>
  </div>
</div>

<!-- FORUM PAGE -->
<div class="page" id="page-forum">
  <div class="section">
    <div class="section-header">
      <div>
        <div class="section-title">💬 Farmer Community</div>
        <div class="section-sub">Discuss, share, and learn from fellow farmers</div>
      </div>
      <button class="new-post-btn" onclick="openNewPost()"><i class="fa fa-pen"></i> New Post</button>
    </div>
    <div id="forumPosts"></div>
  </div>
</div>

<!-- CHAT PAGE -->
<div class="page" id="page-chat">
  <div class="section">
    <div class="section-header">
      <div class="section-title">💬 Messages</div>
    </div>
    <div class="chat-layout">
      <div class="chat-sidebar">
        <div class="chat-sidebar-header"><i class="fa fa-comments" style="color:var(--green-600)"></i> Conversations</div>
        <div id="chatList"></div>
      </div>
      <div class="chat-main">
        <div class="chat-main-header" id="chatMainHeader">
          <div class="ci-avatar">🌾</div>
          <div>
            <div style="font-weight:700;font-size:15px;" id="chatPartnerName">Select a conversation</div>
            <div style="font-size:12px;color:var(--green-600);"><i class="fa fa-circle" style="font-size:8px;"></i> Online</div>
          </div>
        </div>
        <div class="chat-messages" id="chatMessages">
          <div style="text-align:center;padding:40px;color:var(--text3);">
            <div style="font-size:48px;margin-bottom:12px;">💬</div>
            <div style="font-size:16px;font-weight:600;">Start a conversation</div>
            <div style="font-size:13px;margin-top:6px;">Select a contact from the left to chat</div>
          </div>
        </div>
        <div class="chat-input-area">
          <textarea class="chat-input" id="chatInput" placeholder="Type a message..." rows="1" onkeypress="handleChatKey(event)"></textarea>
          <button class="chat-send-btn" onclick="sendMessage()"><i class="fa fa-paper-plane"></i></button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- DASHBOARD PAGE -->
<div class="page" id="page-dashboard">
  <div class="section">
    <div class="dashboard-header" id="dashHeader"></div>
    <div class="dash-stats" id="dashStats"></div>
    <div class="dash-tabs" id="dashTabs"></div>
    <div id="dashContents"></div>
  </div>
</div>

<!-- ADMIN PAGE -->
<div class="page" id="page-admin">
  <div class="section">
    <div class="section-header">
      <div class="section-title">⚙️ Admin Dashboard</div>
    </div>
    <div class="admin-grid">
      <div class="admin-card"><div class="ac-icon green"><i class="fa fa-users"></i></div><div><div class="ac-num">2,41,456</div><div class="ac-label">Total Users</div></div></div>
      <div class="admin-card"><div class="ac-icon orange"><i class="fa fa-tractor"></i></div><div><div class="ac-num">18,234</div><div class="ac-label">Equipment Listed</div></div></div>
      <div class="admin-card"><div class="ac-icon blue"><i class="fa fa-wheat-awn"></i></div><div><div class="ac-num">94,201</div><div class="ac-label">Crop Listings</div></div></div>
      <div class="admin-card"><div class="ac-icon purple"><i class="fa fa-indian-rupee-sign"></i></div><div><div class="ac-num">₹840Cr</div><div class="ac-label">GMV</div></div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;flex-wrap:wrap;" id="adminGrid">
      <div style="background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;">
        <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:16px;">Recent Users</div>
        <table style="width:100%;font-size:13px;border-collapse:collapse;" id="adminUsersTable"></table>
      </div>
      <div style="background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:20px;">
        <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:16px;">Dispute Management</div>
        <div id="adminDisputes"></div>
      </div>
    </div>
  </div>
</div>

</div><!-- end app-container -->

<!-- MOBILE NAV -->
<nav class="mobile-nav">
  <div class="mn-items">
    <button class="mn-item active" onclick="showPage('home')"><i class="fa fa-home"></i><span>Home</span></button>
    <button class="mn-item" onclick="showPage('equipment')"><i class="fa fa-tractor"></i><span>Equipment</span></button>
    <button class="mn-item" onclick="showPage('marketplace')"><i class="fa fa-store"></i><span>Market</span></button>
    <button class="mn-item" onclick="showPage('weather')"><i class="fa fa-cloud-sun"></i><span>Weather</span></button>
    <button class="mn-item" onclick="showPage('forum')"><i class="fa fa-comments"></i><span>Forum</span></button>
    <button class="mn-item" onclick="handleUserClick()"><i class="fa fa-user"></i><span>Profile</span></button>
  </div>
</nav>

<!-- AUTH MODAL -->
<div class="modal-overlay" id="authModal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('authModal')">×</button>
    <div id="authContent"></div>
  </div>
</div>

<!-- BOOKING MODAL -->
<div class="modal-overlay" id="bookingModal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('bookingModal')">×</button>
    <div class="modal-title">📋 Book Now</div>
    <div class="modal-sub">Complete your booking below</div>
    <div id="bookingContent"></div>
  </div>
</div>

<!-- NEW POST MODAL -->
<div class="modal-overlay" id="postModal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('postModal')">×</button>
    <div class="modal-title">✍️ New Forum Post</div>
    <div class="modal-sub">Share your knowledge with the community</div>
    <div class="form-group">
      <label class="form-label">Title</label>
      <input type="text" class="form-input" id="postTitle" placeholder="What do you want to discuss?">
    </div>
    <div class="form-group">
      <label class="form-label">Content</label>
      <textarea class="form-input" id="postContent" rows="5" placeholder="Share your experience, tips, or questions..."></textarea>
    </div>
    <div class="form-group">
      <label class="form-label">Tags (comma separated)</label>
      <input type="text" class="form-input" id="postTags" placeholder="wheat, Punjab, tips">
    </div>
    <button class="btn-primary" style="width:100%;padding:14px;" onclick="submitPost()">Post to Community</button>
  </div>
</div>

<!-- TOAST CONTAINER -->
<div class="toast-container" id="toastContainer"></div>

<!-- FOOTER -->
<footer>
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="logo">
        <div class="logo-icon">🌾</div>
        <div class="logo-text">AgroLink</div>
      </div>
      <p>India's most trusted agriculture platform connecting 2.4 lakh+ farmers with buyers, equipment owners, and transport providers.</p>
    </div>
    <div class="footer-col">
      <h4>Platform</h4>
      <a onclick="showPage('equipment')">Equipment Rental</a>
      <a onclick="showPage('marketplace')">Crop Marketplace</a>
      <a onclick="showPage('transport')">Transport Booking</a>
      <a onclick="showPage('labor')">Labor Hiring</a>
    </div>
    <div class="footer-col">
      <h4>Resources</h4>
      <a onclick="showPage('weather')">Weather & Mandi</a>
      <a onclick="showPage('forum')">Farmer Forum</a>
      <a>Crop Calendar</a>
      <a>Government Schemes</a>
    </div>
    <div class="footer-col">
      <h4>Support</h4>
      <a>Help Centre</a>
      <a>Contact Us</a>
      <a>Privacy Policy</a>
      <a>Terms of Service</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2024 AgroLink Technologies Pvt. Ltd. All rights reserved.</span>
    <span>Made with ❤️ for Indian Farmers</span>
  </div>
</footer>

<script>
// ======== STATE ========
let currentUser = null;
let currentPage = 'home';
let currentChatRoom = null;
let chatData = {};
let darkMode = false;
let notifOpen = false;

const DEMO_CHATS = [
  {id:'c1',name:'Singh Tractors',avatar:'🚜',role:'equipment_owner',preview:'Tractor is available from Dec 1',time:'10m',unread:2},
  {id:'c2',name:'Priya Exports',avatar:'🏪',role:'buyer',preview:'Interested in your Basmati Rice',time:'2h',unread:1},
  {id:'c3',name:'FastCrop Logistics',avatar:'🚛',role:'transport',preview:'Can deliver by tomorrow morning',time:'1d',unread:0},
  {id:'c4',name:'AgroLink Support',avatar:'🌾',role:'support',preview:'How can we help you today?',time:'2d',unread:0},
];

const WEATHER_DATA = [
  {city:'Delhi',temp:22,feels:20,humidity:65,wind:12,icon:'⛅',desc:'Partly Cloudy',rain:'10%'},
  {city:'Punjab',temp:18,feels:16,humidity:72,wind:8,icon:'🌤️',desc:'Mostly Clear',rain:'5%'},
  {city:'Maharashtra',temp:28,feels:31,humidity:78,wind:15,icon:'🌧️',desc:'Light Rain',rain:'70%'},
  {city:'UP',temp:20,feels:19,humidity:68,wind:10,icon:'☀️',desc:'Sunny',rain:'0%'},
];

const MANDI_DATA = [
  {crop:'Wheat',mandi:'Amritsar',price:2350,change:+45,msp:2275},
  {crop:'Paddy (Basmati)',mandi:'Karnal',price:4200,change:+120,msp:2183},
  {crop:'Soybean',mandi:'Indore',price:5100,change:-80,msp:4892},
  {crop:'Cotton',mandi:'Yavatmal',price:7200,change:+200,msp:6620},
  {crop:'Onion',mandi:'Lasalgaon',price:1800,change:-300,msp:0},
  {crop:'Tomato',mandi:'Azadpur',price:2200,change:+500,msp:0},
  {crop:'Sugarcane',mandi:'Kolhapur',price:320,change:+5,msp:315},
  {crop:'Maize',mandi:'Nizamabad',price:2100,change:+35,msp:2090},
];

// ======== PAGE ROUTING ========
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const pg = document.getElementById('page-' + name);
  if(pg) { pg.classList.add('active'); currentPage = name; }
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.mn-item').forEach(b => b.classList.remove('active'));
  const navBtns = document.querySelectorAll('.nav-btn');
  navBtns.forEach(b => { if(b.getAttribute('onclick') && b.getAttribute('onclick').includes("'"+name+"'")) b.classList.add('active'); });
  const mnBtns = document.querySelectorAll('.mn-item');
  mnBtns.forEach(b => { if(b.getAttribute('onclick') && b.getAttribute('onclick').includes("'"+name+"'")) b.classList.add('active'); });
  window.scrollTo(0,0);
  renderPage(name);
  closeAllPanels();
}

function renderPage(name) {
  if(name==='equipment') renderEquipment();
  if(name==='marketplace') renderMarketplace();
  if(name==='transport') renderTransport();
  if(name==='labor') renderLabor();
  if(name==='weather') renderWeather();
  if(name==='forum') renderForum();
  if(name==='chat') renderChat();
  if(name==='dashboard') renderDashboard();
  if(name==='admin') renderAdmin();
}

// ======== EQUIPMENT ========
function renderEquipment(data) {
  const grid = document.getElementById('equipmentGrid');
  if(!grid) return;
  const eq = data || getFilteredEquipment();
  grid.innerHTML = eq.map(e => `
    <div class="card" onclick="openBooking('equipment',${JSON.stringify(e).replace(/"/g,'&quot;')})">
      <div class="card-img">
        ${e.image}
        <span class="card-badge ${e.available?'badge-available':'badge-unavailable'}">${e.available?'✓ Available':'✗ Booked'}</span>
      </div>
      <div class="card-body">
        <div class="card-title">${e.name}</div>
        <div class="card-meta">
          <span><i class="fa fa-location-dot"></i> ${e.location}</span>
          <span><i class="fa fa-user"></i> ${e.owner_name}</span>
          ${e.hp>0?`<span><i class="fa fa-gauge-high"></i> ${e.hp}HP</span>`:''}
        </div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:12px;">${e.description.substring(0,80)}...</div>
        <div class="card-price">₹${e.price.toLocaleString()} <span>/ ${e.unit}</span></div>
        <div class="card-footer">
          <div class="rating">⭐ ${e.rating} <span style="color:var(--text3);font-weight:400">(${e.reviews})</span></div>
          <button class="btn-sm ${e.available?'btn-green':'btn-outline'}" onclick="event.stopPropagation();${e.available?'openBooking(\'equipment\','+JSON.stringify(e).replace(/"/g,'&quot;')+')':'showToast(\'Currently unavailable\',\'warning\')'}">${e.available?'Book Now':'Unavailable'}</button>
        </div>
      </div>
    </div>
  `).join('');
}

function getFilteredEquipment() {
  const search = (document.getElementById('eqSearch')||{}).value||'';
  const cat = (document.getElementById('eqCategory')||{}).value||'';
  const avail = (document.getElementById('eqAvail')||{}).value||'';
  return equipmentData.filter(e => {
    const matchSearch = !search || e.name.toLowerCase().includes(search.toLowerCase()) || e.location.toLowerCase().includes(search.toLowerCase());
    const matchCat = !cat || e.category===cat;
    const matchAvail = !avail || (avail==='available'&&e.available) || (avail==='unavailable'&&!e.available);
    return matchSearch&&matchCat&&matchAvail;
  });
}
function filterEquipment() { renderEquipment(); }

// ======== MARKETPLACE ========
function renderMarketplace() {
  const emGrid = document.getElementById('emergencyGrid');
  const cGrid = document.getElementById('cropsGrid');
  if(!emGrid||!cGrid) return;
  const emergency = cropData.filter(c=>c.emergency);
  const all = getFilteredCrops();
  emGrid.innerHTML = emergency.map(c => cropCard(c)).join('');
  cGrid.innerHTML = all.map(c => cropCard(c)).join('');
}

function cropCard(c) {
  return `
    <div class="card" onclick="openCropDetail(${JSON.stringify(c).replace(/"/g,'&quot;')})">
      <div class="card-img">
        ${c.image}
        ${c.emergency?'<span class="card-badge badge-emergency">⚡ URGENT SALE</span>':''}
        ${!c.emergency?`<span class="card-badge badge-fresh">✓ ${c.freshness}</span>`:''}
      </div>
      <div class="card-body">
        <div class="card-title">${c.name}</div>
        <div class="card-meta">
          <span><i class="fa fa-location-dot"></i> ${c.location}</span>
          <span><i class="fa fa-user"></i> ${c.farmer_name}</span>
          <span><i class="fa fa-boxes-stacked"></i> ${c.quantity} kg</span>
        </div>
        <div class="card-price">₹${c.price} <span>/ kg</span></div>
        <div class="card-footer">
          <div class="rating">⭐ ${c.rating} ${c.verified?'<span style="color:var(--green-600);font-size:11px;">✓ Verified</span>':''}</div>
          <div style="display:flex;gap:6px;">
            <button class="btn-sm btn-outline" onclick="event.stopPropagation();openChat('${c.farmer_name}')"><i class="fa fa-message"></i></button>
            <button class="btn-sm btn-green" onclick="event.stopPropagation();openBooking('crop',${JSON.stringify(c).replace(/"/g,'&quot;')})">Buy Now</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function getFilteredCrops() {
  const search = (document.getElementById('cropSearch')||{}).value||'';
  const cat = (document.getElementById('cropCategory')||{}).value||'';
  return cropData.filter(c => {
    const matchSearch = !search || c.name.toLowerCase().includes(search.toLowerCase());
    const matchCat = !cat || c.category===cat;
    return matchSearch&&matchCat;
  });
}
function filterCrops(type) {
  if(type==='emergency') {
    document.getElementById('cropSearch').value='';
    document.getElementById('cropCategory').value='';
  }
  renderMarketplace();
}

// ======== TRANSPORT ========
function renderTransport() {
  const grid = document.getElementById('transportGrid');
  if(!grid) return;
  grid.innerHTML = transportData.map(t => `
    <div class="card">
      <div class="card-img">${t.image}<span class="card-badge ${t.available?'badge-available':'badge-unavailable'}">${t.available?'✓ Available':'Busy'}</span></div>
      <div class="card-body">
        <div class="card-title">${t.name}</div>
        <div class="card-meta">
          <span><i class="fa fa-location-dot"></i> ${t.location}</span>
          <span><i class="fa fa-weight-hanging"></i> ${t.capacity}</span>
          <span><i class="fa fa-truck"></i> ${t.type}</span>
        </div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:12px;">${t.description}</div>
        <div class="card-price">₹${t.price.toLocaleString()} <span>/ ${t.unit}</span></div>
        <div class="card-footer">
          <div class="rating">⭐ ${t.rating} (${t.reviews})</div>
          <button class="btn-sm btn-green" onclick="openBooking('transport',${JSON.stringify(t).replace(/"/g,'&quot;')})">Book</button>
        </div>
      </div>
    </div>
  `).join('');
}

// ======== LABOR ========
function renderLabor() {
  const grid = document.getElementById('laborGrid');
  if(!grid) return;
  grid.innerHTML = laborData.map(l => `
    <div class="card">
      <div class="card-img">${l.image}<span class="card-badge ${l.available?'badge-available':'badge-unavailable'}">${l.available?'✓ Available':'Hired'}</span></div>
      <div class="card-body">
        <div class="card-title">${l.name}</div>
        <div class="card-meta">
          <span><i class="fa fa-location-dot"></i> ${l.location}</span>
          <span><i class="fa fa-users"></i> ${l.workers} workers</span>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
          ${l.skills.map(s=>`<span style="background:var(--green-100);color:var(--green-800);padding:3px 8px;border-radius:99px;font-size:11px;">${s}</span>`).join('')}
        </div>
        <div style="font-size:13px;color:var(--text2);margin-bottom:12px;">${l.description}</div>
        <div class="card-price">₹${l.daily_rate} <span>/ worker / day</span></div>
        <div class="card-footer">
          <div class="rating">⭐ ${l.rating} (${l.reviews})</div>
          <button class="btn-sm btn-green" onclick="openBooking('labor',${JSON.stringify(l).replace(/"/g,'&quot;')})">Hire</button>
        </div>
      </div>
    </div>
  `).join('');
}

// ======== WEATHER ========
function renderWeather() {
  const grid = document.getElementById('weatherGrid');
  if(grid) grid.innerHTML = WEATHER_DATA.map(w => `
    <div class="weather-card">
      <div class="wc-icon">${w.icon}</div>
      <div class="wc-temp">${w.temp}°C</div>
      <div class="wc-city">${w.city}</div>
      <div class="wc-desc">${w.desc}</div>
      <div class="weather-details">
        <span>💧 ${w.humidity}%</span>
        <span>💨 ${w.wind}km/h</span>
        <span>🌧️ ${w.rain}</span>
      </div>
    </div>
  `).join('');
  const tbody = document.querySelector('#mandiTable tbody');
  if(tbody) tbody.innerHTML = MANDI_DATA.map(m => `
    <tr>
      <td><strong>${m.crop}</strong></td>
      <td>${m.mandi}</td>
      <td><strong>₹${m.price}</strong></td>
      <td class="${m.change>=0?'price-up':'price-down'}">${m.change>=0?'▲':'▼'} ₹${Math.abs(m.change)}</td>
      <td>${m.msp>0?'₹'+m.msp:'N/A'}</td>
    </tr>
  `).join('');
  const mt = document.getElementById('mandiTime');
  if(mt) mt.textContent = new Date().toLocaleTimeString('en-IN');
}

// ======== FORUM ========
function renderForum() {
  const container = document.getElementById('forumPosts');
  if(!container) return;
  container.innerHTML = forumData.map((post,i) => `
    <div class="forum-post" id="post-${post.id}">
      <div class="fp-header">
        <div class="fp-avatar">${post.avatar}</div>
        <div class="fp-meta">
          <div class="fp-author">${post.author_name}</div>
          <div class="fp-time">${post.time}</div>
        </div>
        <span style="background:var(--green-100);color:var(--green-700);padding:3px 10px;border-radius:99px;font-size:11px;">EN</span>
      </div>
      <div class="fp-title">${post.title}</div>
      <div class="fp-content">${post.content.substring(0,200)}${post.content.length>200?'...':''}</div>
      <div class="fp-tags">${post.tags.map(t=>`<span class="fp-tag">#${t}</span>`).join('')}</div>
      <div class="fp-actions">
        <button class="fp-action" onclick="likePost('${post.id}',this)"><i class="fa fa-heart"></i> ${post.likes}</button>
        <button class="fp-action" onclick="toggleComments('${post.id}')"><i class="fa fa-comment"></i> ${post.comments.length} Comments</button>
        <button class="fp-action"><i class="fa fa-share"></i> Share</button>
      </div>
      <div class="fp-comments" id="comments-${post.id}">
        ${post.comments.map(c=>`
          <div class="fp-comment">
            <div class="fc-avatar">👤</div>
            <div class="fc-body">
              <div class="fc-author">${c.author}</div>
              <div class="fc-text">${c.text}</div>
            </div>
          </div>
        `).join('')}
        <div class="fp-comment">
          <div class="fc-avatar">👤</div>
          <div style="flex:1;display:flex;gap:8px;">
            <input type="text" class="search-input" placeholder="Write a comment..." id="commentInput-${post.id}" style="flex:1;padding:8px 12px;" onkeypress="if(event.key==='Enter')addComment('${post.id}')">
            <button class="btn-sm btn-green" onclick="addComment('${post.id}')">Post</button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

function likePost(id, btn) {
  const post = forumData.find(p=>p.id===id);
  if(post) {
    post.likes++;
    btn.innerHTML = `<i class="fa fa-heart"></i> ${post.likes}`;
    btn.classList.add('liked');
    showToast('❤️ Post liked!');
  }
}

function toggleComments(id) {
  const el = document.getElementById('comments-'+id);
  if(el) el.style.display = el.style.display==='block'?'none':'block';
}

function addComment(postId) {
  const input = document.getElementById('commentInput-'+postId);
  if(!input||!input.value.trim()) return;
  const post = forumData.find(p=>p.id===postId);
  if(post) {
    post.comments.push({author: currentUser?currentUser.name:'Guest', text:input.value.trim(), time:'Just now'});
    input.value='';
    renderForum();
    toggleComments(postId);
    showToast('💬 Comment added!');
  }
}

// ======== CHAT ========
function renderChat() {
  const chatList = document.getElementById('chatList');
  if(!chatList) return;
  chatList.innerHTML = DEMO_CHATS.map(c => `
    <div class="chat-item ${currentChatRoom===c.id?'active':''}" onclick="openChatRoom('${c.id}','${c.name}','${c.avatar}')">
      <div class="ci-avatar">${c.avatar}</div>
      <div class="ci-info">
        <div class="ci-name">${c.name}</div>
        <div class="ci-preview">${c.preview}</div>
      </div>
      <div class="ci-meta">
        <div class="ci-time">${c.time}</div>
        ${c.unread>0?`<div class="ci-unread">${c.unread}</div>`:''}
      </div>
    </div>
  `).join('');
}

function openChatRoom(roomId, name, avatar) {
  currentChatRoom = roomId;
  document.getElementById('chatPartnerName').textContent = name;
  const header = document.getElementById('chatMainHeader');
  header.querySelector('.ci-avatar').textContent = avatar;
  if(!chatData[roomId]) {
    chatData[roomId] = getDefaultMessages(roomId, name);
  }
  renderMessages();
  renderChat();
}

function getDefaultMessages(roomId, name) {
  const defaults = {
    c1:[
      {from:'them',text:'Hello! I saw your inquiry about the John Deere tractor.',time:'9:30 AM'},
      {from:'them',text:'It is available from December 1st. Are you interested?',time:'9:31 AM'},
      {from:'me',text:'Yes! I need it for 3 days for wheat harvesting.',time:'9:45 AM'},
      {from:'them',text:'Perfect. Rate is ₹1200/day. Total ₹3600 + transport.',time:'9:47 AM'},
    ],
    c2:[
      {from:'them',text:'Hi! I am interested in your Basmati Rice listing.',time:'2 days ago'},
      {from:'them',text:'Can you offer ₹48/kg for 2000 kg?',time:'2 days ago'},
      {from:'me',text:'Minimum ₹45/kg. For bulk 2000kg, I can do ₹46.',time:'2 days ago'},
      {from:'them',text:'Deal! Please share your bank details for advance payment.',time:'Yesterday'},
    ],
    c3:[
      {from:'them',text:'FastCrop Logistics here. We can deliver your crop order.',time:'1 day ago'},
      {from:'me',text:'Great! Pickup from Karnal, delivery to Delhi mandi.',time:'1 day ago'},
      {from:'them',text:'Refrigerated truck available. Can deliver by tomorrow 6 AM.',time:'1 day ago'},
    ],
    c4:[
      {from:'them',text:'👋 Welcome to AgroLink! How can we help you today?',time:'3 days ago'},
      {from:'me',text:'I need help with listing my crops on the marketplace.',time:'3 days ago'},
      {from:'them',text:'Sure! Go to Marketplace → Click "+ List Crop" → Fill the form. It\'s easy!',time:'3 days ago'},
    ]
  };
  return defaults[roomId] || [];
}

function renderMessages() {
  const container = document.getElementById('chatMessages');
  if(!container||!currentChatRoom) return;
  const msgs = chatData[currentChatRoom]||[];
  container.innerHTML = msgs.map(m=>`
    <div class="msg ${m.from==='me'?'sent':'recv'}">
      <div class="msg-bubble">${m.text}</div>
      <div class="msg-time">${m.time}</div>
    </div>
  `).join('');
  container.scrollTop = container.scrollHeight;
}

function handleChatKey(e) {
  if(e.key==='Enter'&&!e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  if(!input||!input.value.trim()) return;
  if(!currentChatRoom) { showToast('Please select a conversation first','warning'); return; }
  if(!chatData[currentChatRoom]) chatData[currentChatRoom]=[];
  const now = new Date();
  chatData[currentChatRoom].push({from:'me',text:input.value.trim(),time:now.getHours()+':'+String(now.getMinutes()).padStart(2,'0')});
  input.value='';
  renderMessages();
  // Simulate reply after 1.5s
  const room = currentChatRoom;
  const replies = ['Thanks for your message!','I\'ll get back to you shortly.','Sounds good, let me check.','Can you share more details?','I\'ll confirm and let you know.'];
  setTimeout(()=>{
    if(chatData[room]) {
      chatData[room].push({from:'them',text:replies[Math.floor(Math.random()*replies.length)],time:now.getHours()+':'+String(now.getMinutes()+1).padStart(2,'0')});
      if(currentChatRoom===room) renderMessages();
    }
  },1500);
}

function openChat(name) {
  const chat = DEMO_CHATS.find(c=>c.name===name)||{id:'c'+Date.now(),name,avatar:'👤'};
  showPage('chat');
  setTimeout(()=>openChatRoom(chat.id,chat.name,chat.avatar),100);
}

// ======== DASHBOARD ========
function renderDashboard() {
  if(!currentUser) { showPage('home'); openAuth('login'); return; }
  const dh = document.getElementById('dashHeader');
  const ds = document.getElementById('dashStats');
  const dt = document.getElementById('dashTabs');
  const dc = document.getElementById('dashContents');
  if(!dh) return;
  const role = currentUser.role;
  dh.innerHTML = `
    <div class="dh-greeting">Good day! 👋</div>
    <div class="dh-name">${currentUser.name}</div>
    <div><span class="dh-role">${roleIcon(role)} ${roleLabel(role)}</span></div>
  `;
  const stats = getDashStats(role);
  ds.innerHTML = stats.map(s=>`
    <div class="dash-stat">
      <div class="ds-icon">${s.icon}</div>
      <div class="ds-num">${s.num}</div>
      <div class="ds-label">${s.label}</div>
    </div>
  `).join('');
  const tabs = getDashTabs(role);
  dt.innerHTML = tabs.map((t,i)=>`<button class="dash-tab ${i===0?'active':''}" onclick="switchDashTab(${i})">${t.label}</button>`).join('');
  dc.innerHTML = tabs.map((t,i)=>`<div class="dash-content ${i===0?'active':''}" id="dashTab-${i}">${t.content}</div>`).join('');
}

function getDashStats(role) {
  const maps = {
    farmer:[{icon:'🌾',num:'12',label:'Active Listings'},{icon:'₹',num:'₹2.4L',label:'Total Earnings'},{icon:'📦',num:'8',label:'Orders'},{icon:'⭐',num:'4.8',label:'Rating'}],
    buyer:[{icon:'🛒',num:'34',label:'Total Orders'},{icon:'₹',num:'₹18L',label:'Spent'},{icon:'🤝',num:'12',label:'Suppliers'},{icon:'⭐',num:'4.6',label:'Rating'}],
    equipment_owner:[{icon:'🚜',num:'5',label:'Equipment Listed'},{icon:'₹',num:'₹85K',label:'Monthly Revenue'},{icon:'📅',num:'23',label:'Bookings'},{icon:'⭐',num:'4.9',label:'Rating'}],
    transport:[{icon:'🚛',num:'3',label:'Vehicles'},{icon:'₹',num:'₹42K',label:'Monthly Revenue'},{icon:'📍',num:'67',label:'Trips Done'},{icon:'⭐',num:'4.7',label:'Rating'}],
    admin:[{icon:'👥',num:'2.4L',label:'Total Users'},{icon:'₹',num:'₹840Cr',label:'GMV'},{icon:'⚠️',num:'14',label:'Disputes'},{icon:'📈',num:'+23%',label:'Growth'}],
  };
  return maps[role]||maps.farmer;
}

function getDashTabs(role) {
  if(role==='farmer') return [
    {label:'📋 My Listings',content:`<div class="cards-grid">${cropData.slice(0,3).map(c=>cropCard(c)).join('')}</div>`},
    {label:'📦 Orders',content:'<div style="padding:20px;text-align:center;color:var(--text3)">No pending orders</div>'},
    {label:'💰 Earnings',content:`<div style="text-align:center;padding:40px;"><div style="font-size:48px">💰</div><div style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:var(--green-700);margin:12px 0">₹2,40,000</div><div style="color:var(--text3)">Total earnings this season</div></div>`},
  ];
  if(role==='equipment_owner') return [
    {label:'🚜 My Equipment',content:`<div class="cards-grid">${equipmentData.filter(e=>e.owner==='owner1').map(e=>`<div class="card"><div class="card-img">${e.image}</div><div class="card-body"><div class="card-title">${e.name}</div><div class="card-price">₹${e.price}/${e.unit}</div></div></div>`).join('')}</div>`},
    {label:'📅 Bookings',content:'<div style="padding:20px;text-align:center;color:var(--text3)">No upcoming bookings</div>'},
  ];
  return [
    {label:'📊 Overview',content:`<div style="text-align:center;padding:40px;"><div style="font-size:48px">📊</div><div style="font-size:16px;color:var(--text3);margin-top:12px">Dashboard content for ${roleLabel(currentUser.role)}</div></div>`},
    {label:'⚙️ Settings',content:`<div style="padding:20px;"><div class="form-group"><label class="form-label">Display Name</label><input class="form-input" value="${currentUser.name}"></div><div class="form-group"><label class="form-label">Location</label><input class="form-input" value="${currentUser.location}"></div><button class="btn-primary" onclick="showToast('Profile updated!')">Save Changes</button></div>`},
  ];
}

function switchDashTab(idx) {
  document.querySelectorAll('.dash-tab').forEach((t,i)=>t.classList.toggle('active',i===idx));
  document.querySelectorAll('.dash-content').forEach((c,i)=>c.classList.toggle('active',i===idx));
}

// ======== ADMIN ========
function renderAdmin() {
  const table = document.getElementById('adminUsersTable');
  if(table) {
    const users = Object.entries(usersData).slice(0,6);
    table.innerHTML = `<tr style="background:var(--green-50);"><th style="padding:8px;text-align:left;font-size:12px;">Name</th><th style="padding:8px;text-align:left;font-size:12px;">Role</th><th style="padding:8px;text-align:left;font-size:12px;">Status</th></tr>` +
    users.map(([k,v])=>`<tr style="border-bottom:1px solid var(--border);"><td style="padding:8px;font-size:13px;">${v.avatar} ${v.name}</td><td style="padding:8px;font-size:12px;text-transform:capitalize;">${roleLabel(v.role)}</td><td style="padding:8px;"><span style="background:var(--green-100);color:var(--green-700);padding:2px 8px;border-radius:99px;font-size:11px;">Active</span></td></tr>`).join('');
  }
  const disputes = document.getElementById('adminDisputes');
  if(disputes) {
    disputes.innerHTML = ['Payment dispute - Ramesh vs Priya (₹45,000)','Equipment damage claim - Singh Tractors (₹12,000)','Late delivery complaint - FastCrop Logistics'].map(d=>`
      <div style="padding:12px;border:1px solid var(--border);border-radius:var(--radius-sm);margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;">
        <div style="font-size:13px;">${d}</div>
        <div style="display:flex;gap:6px;"><button class="btn-sm btn-green" style="padding:4px 10px;font-size:11px;" onclick="showToast('Dispute resolved')">Resolve</button></div>
      </div>
    `).join('');
  }
}

// ======== BOOKING ========
function openBooking(type, item) {
  if(!currentUser) { openAuth('login'); return; }
  const content = document.getElementById('bookingContent');
  const typeLabel = {equipment:'Equipment',crop:'Crop',transport:'Transport',labor:'Labor'};
  content.innerHTML = `
    <div class="bk-summary">
      <div class="bk-item-name">${item.image||'📋'} ${item.name}</div>
      <div class="bk-price">₹${item.price} / ${item.unit||'unit'} • ${item.location}</div>
    </div>
    ${type==='equipment'?`
      <div class="form-group"><label class="form-label">Start Date</label><input type="date" class="form-input" id="bkStart" min="${new Date().toISOString().split('T')[0]}"></div>
      <div class="form-group"><label class="form-label">End Date</label><input type="date" class="form-input" id="bkEnd"></div>
      <div class="form-group"><label class="form-label">Special Requirements</label><textarea class="form-input" rows="2" placeholder="Any special requirements..."></textarea></div>
    `:''}
    ${type==='crop'?`
      <div class="form-group"><label class="form-label">Quantity (kg)</label><input type="number" class="form-input" id="bkQty" placeholder="Enter quantity" max="${item.quantity}"></div>
      <div class="form-group"><label class="form-label">Delivery Address</label><input type="text" class="form-input" placeholder="Enter delivery address"></div>
    `:''}
    ${type==='transport'?`
      <div class="form-group"><label class="form-label">Pickup Location</label><input type="text" class="form-input" placeholder="From where?"></div>
      <div class="form-group"><label class="form-label">Delivery Location</label><input type="text" class="form-input" placeholder="Where to deliver?"></div>
      <div class="form-group"><label class="form-label">Pickup Date</label><input type="date" class="form-input"></div>
    `:''}
    ${type==='labor'?`
      <div class="form-group"><label class="form-label">Number of Workers Needed</label><input type="number" class="form-input" placeholder="e.g. 5"></div>
      <div class="form-group"><label class="form-label">Duration (days)</label><input type="number" class="form-input" placeholder="Number of days"></div>
      <div class="form-group"><label class="form-label">Work Location</label><input type="text" class="form-input" placeholder="Your farm location"></div>
    `:''}
    <div style="background:var(--green-50);border-radius:var(--radius-sm);padding:12px;margin-bottom:16px;">
      <div style="font-size:12px;color:var(--text3);margin-bottom:4px;">Payment via</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer;"><input type="radio" name="payment" checked> Razorpay</label>
        <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer;"><input type="radio" name="payment"> UPI Direct</label>
        <label style="display:flex;align-items:center;gap:6px;font-size:13px;cursor:pointer;"><input type="radio" name="payment"> Cash on Delivery</label>
      </div>
    </div>
    <button class="btn-primary" style="width:100%;padding:14px;" onclick="confirmBooking('${type}','${item.name}',${item.price})">
      💳 Confirm & Pay ₹${item.price}
    </button>
  `;
  openModal('bookingModal');
}

function confirmBooking(type, name, price) {
  closeModal('bookingModal');
  showToast(`✅ ${name} booked successfully! Payment of ₹${price} processed via Razorpay.`);
  setTimeout(()=>showToast('📲 Booking confirmation sent to your registered mobile number.'),2000);
}

// ======== AUTH ========
function openAuth(mode) {
  const content = document.getElementById('authContent');
  if(mode==='login') {
    content.innerHTML = `
      <div class="modal-title">👋 Welcome Back</div>
      <div class="modal-sub">Sign in to your AgroLink account</div>
      <div class="demo-accounts">
        <h4>Demo Accounts</h4>
        <p>
          Farmer: farmer1 / pass123<br>
          Buyer: buyer1 / pass123<br>
          Equipment Owner: owner1 / pass123<br>
          Transport: transport1 / pass123<br>
          Admin: admin / admin123
        </p>
      </div>
      <div class="form-group"><label class="form-label">Username</label><input type="text" class="form-input" id="loginUser" placeholder="Enter username"></div>
      <div class="form-group"><label class="form-label">Password</label><input type="password" class="form-input" id="loginPass" placeholder="Enter password" onkeypress="if(event.key==='Enter')doLogin()"></div>
      <button class="btn-primary" style="width:100%;padding:14px;" onclick="doLogin()">Sign In</button>
      <div class="auth-toggle">Don't have an account? <a onclick="openAuth('register')">Create one →</a></div>
    `;
  } else {
    content.innerHTML = `
      <div class="modal-title">🌱 Join AgroLink</div>
      <div class="modal-sub">Create your free account today</div>
      <div class="form-group"><label class="form-label">Full Name</label><input type="text" class="form-input" id="regName" placeholder="Your full name"></div>
      <div class="form-group"><label class="form-label">Username</label><input type="text" class="form-input" id="regUser" placeholder="Choose a username"></div>
      <div class="form-group"><label class="form-label">Password</label><input type="password" class="form-input" id="regPass" placeholder="Create password"></div>
      <div class="form-group"><label class="form-label">I am a...</label></div>
      <div class="role-grid">
        <div class="role-option selected" onclick="selectRole(this,'farmer')"><div class="ro-icon">🧑‍🌾</div><div class="ro-text">Farmer</div></div>
        <div class="role-option" onclick="selectRole(this,'buyer')"><div class="ro-icon">🏪</div><div class="ro-text">Buyer</div></div>
        <div class="role-option" onclick="selectRole(this,'equipment_owner')"><div class="ro-icon">🚜</div><div class="ro-text">Equipment Owner</div></div>
        <div class="role-option" onclick="selectRole(this,'transport')"><div class="ro-icon">🚛</div><div class="ro-text">Transporter</div></div>
      </div>
      <input type="hidden" id="regRole" value="farmer">
      <button class="btn-primary" style="width:100%;padding:14px;" onclick="doRegister()">Create Account</button>
      <div class="auth-toggle">Already have an account? <a onclick="openAuth('login')">Sign in →</a></div>
    `;
  }
  openModal('authModal');
}

function selectRole(el, role) {
  document.querySelectorAll('.role-option').forEach(r=>r.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('regRole').value = role;
}

function doLogin() {
  const user = document.getElementById('loginUser').value.trim();
  const pass = document.getElementById('loginPass').value.trim();
  if(!user||!pass) { showToast('Please fill all fields','warning'); return; }
  const userData = usersData[user];
  if(!userData||userData.password!==pass) { showToast('Invalid credentials','error'); return; }
  currentUser = {...userData, username:user};
  updateUserUI();
  closeModal('authModal');
  showToast(`🎉 Welcome back, ${currentUser.name}!`);
  if(user==='admin') { setTimeout(()=>showPage('admin'),500); return; }
  setTimeout(()=>showPage('dashboard'),500);
}

function doRegister() {
  const name = document.getElementById('regName').value.trim();
  const user = document.getElementById('regUser').value.trim();
  const pass = document.getElementById('regPass').value.trim();
  const role = document.getElementById('regRole').value;
  if(!name||!user||!pass) { showToast('Please fill all fields','warning'); return; }
  if(usersData[user]) { showToast('Username already exists','warning'); return; }
  usersData[user] = {password:pass,role,name,location:'India',avatar:roleIcon(role),verified:false,rating:0};
  currentUser = {username:user,...usersData[user]};
  updateUserUI();
  closeModal('authModal');
  showToast(`🌱 Welcome to AgroLink, ${name}!`);
  setTimeout(()=>showPage('dashboard'),500);
}

function updateUserUI() {
  const pill = document.getElementById('userPill');
  const avatar = document.getElementById('headerAvatar');
  const name = document.getElementById('headerName');
  if(currentUser) {
    avatar.textContent = currentUser.avatar;
    name.textContent = currentUser.name.split(' ')[0];
  } else {
    avatar.textContent = '👤';
    name.textContent = 'Login';
  }
}

function handleUserClick() {
  if(currentUser) {
    showPage(currentUser.role==='admin'?'admin':'dashboard');
  } else {
    openAuth('login');
  }
}

function logout() {
  currentUser = null;
  updateUserUI();
  showPage('home');
  showToast('👋 Logged out successfully');
}

// ======== LISTING MODALS ========
function openListEquipment() {
  if(!currentUser) { openAuth('login'); return; }
  alert('Equipment listing form coming soon! In production, this opens a full form to list your equipment.');
  showToast('📋 Listing form will be available here');
}
function openListCrop() {
  if(!currentUser) { openAuth('login'); return; }
  alert('Crop listing form coming soon!');
  showToast('🌾 Crop listing form will be available here');
}
function openListTransport() {
  if(!currentUser) { openAuth('login'); return; }
  showToast('🚛 Transport listing form will be available here');
}
function openListLabor() {
  if(!currentUser) { openAuth('login'); return; }
  showToast('👷 Worker profile form will be available here');
}
function openCropDetail(crop) {
  showToast(`🌾 Viewing ${crop.name} - ₹${crop.price}/kg from ${crop.farmer_name}`);
}
function openNewPost() {
  if(!currentUser) { openAuth('login'); return; }
  openModal('postModal');
}
function submitPost() {
  const title = document.getElementById('postTitle').value.trim();
  const content = document.getElementById('postContent').value.trim();
  if(!title||!content) { showToast('Please fill title and content','warning'); return; }
  const tags = document.getElementById('postTags').value.split(',').map(t=>t.trim()).filter(Boolean);
  forumData.unshift({
    id:'p'+Date.now(),
    author:currentUser.username,
    author_name:currentUser.name,
    avatar:currentUser.avatar,
    title,content,tags,
    likes:0,comments:[],
    time:'Just now',lang:'en'
  });
  closeModal('postModal');
  showPage('forum');
  showToast('✅ Post published to the community!');
}

// ======== UTILS ========
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
function closeAllPanels() {
  notifOpen = false;
  document.getElementById('notifPanel').classList.remove('open');
}
function toggleNotifPanel() {
  notifOpen = !notifOpen;
  document.getElementById('notifPanel').classList.toggle('open', notifOpen);
}
function toggleTheme() {
  darkMode = !darkMode;
  document.documentElement.setAttribute('data-theme', darkMode?'dark':'light');
  document.getElementById('themeIcon').className = darkMode?'fa fa-sun':'fa fa-moon';
}
function showToast(msg, type='success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast' + (type!=='success'?' '+type:'');
  toast.innerHTML = `<span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(()=>{ toast.style.animation='toastOut .3s ease forwards'; setTimeout(()=>toast.remove(),300); }, 3500);
}
function roleIcon(r) { return {farmer:'🧑‍🌾',buyer:'🏪',equipment_owner:'🚜',transport:'🚛',admin:'⚙️',labor:'👷'}[r]||'👤'; }
function roleLabel(r) { return {farmer:'Farmer',buyer:'Buyer',equipment_owner:'Equipment Owner',transport:'Transport Provider',admin:'Administrator',labor:'Farm Worker'}[r]||r; }

// ======== DATA (loaded from Flask) ========
const equipmentData = {{ equipment | tojson }};
const cropData = {{ crops | tojson }};
const transportData = {{ transport | tojson }};
const laborData = {{ labor | tojson }};
const forumData = {{ posts | tojson }};
const usersData = {{ users | tojson }};

// ======== INIT ========
document.addEventListener('DOMContentLoaded', ()=>{
  renderPage('home');
  // Close modals on overlay click
  document.querySelectorAll('.modal-overlay').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)m.classList.remove('open');}));
  // Close notif panel on outside click
  document.addEventListener('click',e=>{
    const panel = document.getElementById('notifPanel');
    if(notifOpen&&!panel.contains(e.target)&&!e.target.closest('.notif-badge')) closeAllPanels();
  });
  setInterval(()=>{
    if(Math.random()<0.3) {
      const notifs = ['🌾 New crop listing near you','🚜 Equipment available for rent','💰 Price update: Wheat ₹2400/qtl','👥 New comment on your forum post'];
      showToast(notifs[Math.floor(Math.random()*notifs.length)]);
    }
  }, 30000);
});
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML,
        equipment=equipment_db,
        crops=crops_db,
        transport=transport_db,
        labor=labor_db,
        posts=posts_db,
        users={k: {kk:vv for kk,vv in v.items() if kk!='password'} for k,v in users_db.items()}
    )

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = users_db.get(data.get('username'))
    if user and user['password'] == data.get('password'):
        return jsonify({'success': True, 'user': {k:v for k,v in user.items() if k!='password'}, 'username': data['username']})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    if username in users_db:
        return jsonify({'success': False, 'error': 'Username exists'}), 400
    users_db[username] = {
        'password': data['password'],
        'role': data.get('role', 'farmer'),
        'name': data['name'],
        'location': data.get('location', 'India'),
        'avatar': '🧑‍🌾',
        'verified': False,
        'rating': 0
    }
    return jsonify({'success': True})

@app.route('/api/chat/send', methods=['POST'])
def send_chat():
    data = request.json
    room = data.get('room_id')
    if room not in messages_db:
        messages_db[room] = []
    msg = {'id': str(uuid.uuid4()), 'text': data['text'], 'from': data['from'], 'time': datetime.now().strftime('%H:%M')}
    messages_db[room].append(msg)
    return jsonify({'success': True, 'message': msg})

@app.route('/api/chat/messages/<room_id>')
def get_messages(room_id):
    return jsonify(messages_db.get(room_id, []))

@app.route('/api/booking', methods=['POST'])
def create_booking():
    data = request.json
    booking = {
        'id': str(uuid.uuid4()),
        'type': data['type'],
        'item_id': data['item_id'],
        'user': data['user'],
        'date': datetime.now().isoformat(),
        'status': 'confirmed'
    }
    bookings_db.append(booking)
    return jsonify({'success': True, 'booking': booking})

@app.route('/api/crops')
def get_crops():
    return jsonify(crops_db)

@app.route('/api/equipment')
def get_equipment():
    return jsonify(equipment_db)

@app.route('/api/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        data = request.json
        post = {
            'id': 'p'+str(uuid.uuid4())[:8],
            'author': data['author'],
            'author_name': data['author_name'],
            'avatar': data.get('avatar', '🧑‍🌾'),
            'title': data['title'],
            'content': data['content'],
            'likes': 0,
            'comments': [],
            'tags': data.get('tags', []),
            'time': 'Just now',
            'lang': 'en'
        }
        posts_db.insert(0, post)
        return jsonify({'success': True, 'post': post})
    return jsonify(posts_db)

@app.route('/api/weather')
def weather():
    return jsonify([
        {'city': 'Delhi', 'temp': 22, 'feels': 20, 'humidity': 65, 'wind': 12, 'desc': 'Partly Cloudy', 'icon': 'cloud-sun'},
        {'city': 'Punjab', 'temp': 18, 'feels': 16, 'humidity': 72, 'wind': 8, 'desc': 'Mostly Clear', 'icon': 'sun'},
        {'city': 'Maharashtra', 'temp': 28, 'feels': 31, 'humidity': 78, 'wind': 15, 'desc': 'Light Rain', 'icon': 'rain'},
        {'city': 'UP', 'temp': 20, 'feels': 19, 'humidity': 68, 'wind': 10, 'desc': 'Sunny', 'icon': 'sun'},
    ])


