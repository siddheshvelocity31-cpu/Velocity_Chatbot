"""Travel and Holiday Package Lookup & Calculation Tool for Gemini Chatbot.

Provides comprehensive holiday estimates including:
- Round-trip travel fares (Train sleeper/3AC/2AC vs Flights)
- Accommodation categorized from Cheapest (Hostels/Budget) to Richest (5-Star Heritage Palaces)
- Total package cost calculator (Travel + Hotel * Nights + Sightseeing/Food)
"""

from typing import Dict, Any, List, Optional
import math

# Comprehensive Travel & Holiday Database
DESTINATIONS_DATA: Dict[str, Dict[str, Any]] = {
    "ujjain": {
        "name": "Ujjain (Mahakaleshwar Jyotirlinga)",
        "tagline": "The Holy City of Mahakal — Jyotirlinga Darshan, Bhasma Aarti & Sacred Ghats",
        "category": "Spiritual & Pilgrimage Destination",
        "best_time_to_visit": "October to March",
        "key_attractions": [
            "Mahakaleshwar Jyotirlinga (Live Bhasma Aarti)", "Mahakal Lok Corridor",
            "Ram Ghat & Evening Shipra River Aarti", "Kal Bhairav Temple (Sacred Offerings)",
            "Harsiddhi Mata Shaktipeeth", "Mangalnath Temple & Sandipani Ashram"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Dharamshala & Ashram Yatri Niwas",
                "name": "Mahakal Bhakt Niwas / Clean Ghat Ashrams",
                "price_per_night_inr": 600,
                "rating": "4.2 ★",
                "amenities": "Clean AC/Non-AC Room, Hot Water, Walking distance to Mahakal Temple, Temple assistance",
                "description": "Ideal for pilgrims, budget families, and solo travelers on spiritual visit."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Comfort",
                "name": "Hotel Imperial Ujjain / Anjushree Courtyard",
                "price_per_night_inr": 2200,
                "rating": "4.4 ★",
                "amenities": "Spacious Deluxe AC Rooms, Pure Veg Restaurant, Temple Pickup Assistance, Wi-Fi",
                "description": "Comfortable family-friendly hotel close to the city center and temples."
            },
            "premium": {
                "tier": "Premium 4-Star Luxury",
                "name": "Hotel Abika Elite / Anjushree Luxury Resort",
                "price_per_night_inr": 5500,
                "rating": "4.6 ★",
                "amenities": "Multi-Cuisine Buffet, Swimming Pool, Spa, VIP Darshan Assistance, Luxury Suite",
                "description": "Premium modern stay with fine dining and complete relaxation."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Heritage Sanctuary",
                "name": "Rudraksh Club & Resort / Shipra Heritage Suite",
                "price_per_night_inr": 14000,
                "rating": "4.8 ★",
                "amenities": "Sprawling Club Villa, Landscaped Gardens, Private Temple Tour, Royal Hospitality",
                "description": "The finest luxury retreat in Ujjain with world-class amenities."
            }
        },
        "transport_from": {
            "mumbai": {
                "train_available": True,
                "train_details": "Avantika Express / Mumbai Indore Duronto (9-11 hrs)",
                "train_roundtrip_sleeper_inr": 650,
                "train_roundtrip_3ac_inr": 1650,
                "train_roundtrip_2ac_inr": 2350,
                "flight_available": True,
                "flight_details": "Flight to Indore Airport (1 hr 15 mins) + 45 mins cab to Ujjain",
                "flight_roundtrip_inr": 4800
            },
            "delhi": {
                "train_available": True,
                "train_details": "Vande Bharat Express / Malwa Express (10-12 hrs)",
                "train_roundtrip_sleeper_inr": 700,
                "train_roundtrip_3ac_inr": 1750,
                "train_roundtrip_2ac_inr": 2500,
                "flight_available": True,
                "flight_details": "Flight to Indore Airport (1 hr 20 mins) + 45 mins cab to Ujjain",
                "flight_roundtrip_inr": 5200
            },
            "ahmedabad": {
                "train_available": True,
                "train_details": "Shanti Express / Vande Bharat (6 hrs)",
                "train_roundtrip_sleeper_inr": 400,
                "train_roundtrip_3ac_inr": 1050,
                "train_roundtrip_2ac_inr": 1500,
                "flight_available": True,
                "flight_details": "Flight to Indore (1 hr) + cab",
                "flight_roundtrip_inr": 4200
            },
            "pune": {
                "train_available": True,
                "train_details": "Pune Indore Superfast Express (12 hrs)",
                "train_roundtrip_sleeper_inr": 650,
                "train_roundtrip_3ac_inr": 1600,
                "train_roundtrip_2ac_inr": 2300,
                "flight_available": True,
                "flight_details": "Flight to Indore (1 hr 15 mins) + cab",
                "flight_roundtrip_inr": 5400
            },
            "bengaluru": {
                "train_available": True,
                "train_details": "Yesvantpur Indore Express (30 hrs)",
                "train_roundtrip_sleeper_inr": 1500,
                "train_roundtrip_3ac_inr": 3800,
                "train_roundtrip_2ac_inr": 5400,
                "flight_available": True,
                "flight_details": "Flight to Indore (2 hrs) + 45 mins cab to Ujjain",
                "flight_roundtrip_inr": 6500
            }
        },
        "daily_food_activities_estimate_inr": 800
    },
    "kashmir": {
        "name": "Kashmir (Srinagar, Gulmarg & Pahalgam)",
        "tagline": "Paradise on Earth — Dal Lake Houseboats, Snow Gondola & Chinar Valleys",
        "category": "Scenic Valleys, Snow & Alpine Paradise",
        "best_time_to_visit": "March to October (Lush Green) / Dec to Feb (Snow & Skiing)",
        "key_attractions": [
            "Dal Lake Shikara Ride & Night Stay on Carved Houseboat",
            "Gulmarg Gondola (World's 2nd Highest Cable Car & Snow Skiing)",
            "Pahalgam Betaab Valley, Aru Valley & Baisaran (Mini Switzerland)",
            "Sonamarg Thajiwas Glacier Trek",
            "Mughal Gardens (Shalimar Bagh, Nishat Bagh & Chashme Shahi)"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Backpacker & Traditional Homestay",
                "name": "Zostel Srinagar / Kashmiri Family Homestay",
                "price_per_night_inr": 1200,
                "rating": "4.3 ★",
                "amenities": "Warm Heated Rooms, Free Wi-Fi, Authentic Kehwa Tea, Traditional Kashmiri Meals",
                "description": "Warm, authentic local Kashmiri hospitality with scenic mountain views."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Deluxe Hotel",
                "name": "Hotel Grand Mumtaz Srinagar / Pine Palace Gulmarg",
                "price_per_night_inr": 3800,
                "rating": "4.5 ★",
                "amenities": "Central Heating, Wooden Architecture, Multi-Cuisine Wazwan Buffet, Garden Views",
                "description": "Cozy and comfortable stay with warm heating and scenic valley locations."
            },
            "premium": {
                "tier": "Premium 4-Star Carved Luxury Houseboat / Resort",
                "name": "Heritage Walnut Houseboat on Nigeen Lake / The Rosewood Gulmarg",
                "price_per_night_inr": 11000,
                "rating": "4.7 ★",
                "amenities": "Hand-Carved Cedar Wood Interiors, Private Shikara Transfers, Personal Chef, Heated Balcony",
                "description": "Exclusive carved houseboat stay on tranquil Nigeen Lake with royal hospitality."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Himalayan Sanctuary",
                "name": "The Khyber Himalayan Resort & Spa Gulmarg / Taj Dal View Srinagar",
                "price_per_night_inr": 34000,
                "rating": "4.9 ★",
                "amenities": "Heated Glass-Enclosed Pool, Ski-in/Ski-out Access, L'Occitane Spa, Panoramic Pine Forest Views",
                "description": "India's premier luxury ski resort set amidst majestic snow-clad Himalayas."
            }
        },
        "transport_from": {
            "delhi": {
                "train_available": True,
                "train_details": "Vande Bharat Express to Jammu/Katra (8 hrs) + Cab to Srinagar (6 hrs)",
                "train_roundtrip_sleeper_inr": 1200,
                "train_roundtrip_3ac_inr": 2800,
                "train_roundtrip_2ac_inr": 4100,
                "flight_available": True,
                "flight_details": "Direct Flight to Srinagar (1 hr 25 mins)",
                "flight_roundtrip_inr": 6500
            },
            "mumbai": {
                "train_available": True,
                "train_details": "Swaraj Express to Jammu (28 hrs) + Cab to Srinagar",
                "train_roundtrip_sleeper_inr": 1800,
                "train_roundtrip_3ac_inr": 4400,
                "train_roundtrip_2ac_inr": 6400,
                "flight_available": True,
                "flight_details": "Direct / 1-Stop Flight to Srinagar (2 hrs 45 mins)",
                "flight_roundtrip_inr": 9800
            },
            "bengaluru": {
                "train_available": False,
                "train_details": "Train to Delhi + Connecting Train to Jammu",
                "flight_available": True,
                "flight_details": "Direct / 1-Stop Flight to Srinagar (3 hrs 30 mins)",
                "flight_roundtrip_inr": 11500
            },
            "pune": {
                "train_available": False,
                "train_details": "Train to Delhi + Train to Jammu",
                "flight_available": True,
                "flight_details": "Connecting Flight to Srinagar (3 hrs)",
                "flight_roundtrip_inr": 10500
            },
            "ahmedabad": {
                "train_available": True,
                "train_details": "Sarvodaya Express to Jammu (24 hrs) + Cab",
                "train_roundtrip_sleeper_inr": 1400,
                "train_roundtrip_3ac_inr": 3600,
                "train_roundtrip_2ac_inr": 5200,
                "flight_available": True,
                "flight_details": "Connecting Flight to Srinagar (2 hrs 30 mins)",
                "flight_roundtrip_inr": 9200
            }
        },
        "daily_food_activities_estimate_inr": 1600
    },

    "goa": {
        "name": "Goa",
        "tagline": "Sun, Sand, Beaches & Vibrant Nightlife",
        "category": "Beach & Leisure Destination",
        "best_time_to_visit": "October to March",
        "key_attractions": [
            "Baga & Calangute Beach", "Dudhsagar Waterfalls", "Aguada Fort",
            "Anjuna Flea Market", "Basilica of Bom Jesus", "Mandovi River Cruise"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Backpacker Hostel",
                "name": "Zostel / Goa Beach Backpackers / Clean Guesthouses",
                "price_per_night_inr": 1200,
                "rating": "4.2 ★",
                "amenities": "AC Dorm / Private Room, Free Wi-Fi, Social Lounge, Beach Walk (5 mins)",
                "description": "Ideal for solo travelers, backpackers, and budget groups."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Comfort",
                "name": "BloomSuites / Lemon Tree Hotel Goa",
                "price_per_night_inr": 3800,
                "rating": "4.5 ★",
                "amenities": "Deluxe AC Room, Swimming Pool, Complimentary Breakfast, Restaurant, Bar",
                "description": "Great for families and couples looking for comfort and great location."
            },
            "premium": {
                "tier": "Premium 4-Star Resort",
                "name": "Novotel Goa Resort & Spa / Radisson Blu Cavelossim",
                "price_per_night_inr": 8500,
                "rating": "4.6 ★",
                "amenities": "Private Balcony, Infinity Pool, Full Spa, Multi-Cuisine Dining, Beach Access",
                "description": "Upscale beachfront resort with premium amenities and evening entertainment."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Heritage / Palace",
                "name": "The Leela Goa / Taj Exotica Resort & Spa / W Goa",
                "price_per_night_inr": 28000,
                "rating": "4.9 ★",
                "amenities": "Private Plunge Pool Villa, 12-Hole Golf Course, Butler Service, Private Beach, Fine Dining",
                "description": "The ultimate royal luxury experience with world-class hospitality."
            }
        },
        "transport_from": {
            "mumbai": {
                "train_available": True,
                "train_details": "Tejas Express / Vande Bharat Express (8-10 hrs)",
                "train_roundtrip_sleeper_inr": 900,
                "train_roundtrip_3ac_inr": 2400,
                "train_roundtrip_2ac_inr": 3600,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 15 mins)",
                "flight_roundtrip_inr": 5500
            },
            "delhi": {
                "train_available": True,
                "train_details": "Goa Rajdhani / Goa Express (24-28 hrs)",
                "train_roundtrip_sleeper_inr": 1600,
                "train_roundtrip_3ac_inr": 4200,
                "train_roundtrip_2ac_inr": 6200,
                "flight_available": True,
                "flight_details": "Direct Flight (2 hrs 30 mins)",
                "flight_roundtrip_inr": 8800
            },
            "bengaluru": {
                "train_available": True,
                "train_details": "Kacheguda/Yesvantpur Vasco Express (13 hrs)",
                "train_roundtrip_sleeper_inr": 850,
                "train_roundtrip_3ac_inr": 2200,
                "train_roundtrip_2ac_inr": 3300,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 10 mins)",
                "flight_roundtrip_inr": 4800
            },
            "pune": {
                "train_available": True,
                "train_details": "Goa Express / Poorna Express (10 hrs)",
                "train_roundtrip_sleeper_inr": 800,
                "train_roundtrip_3ac_inr": 2100,
                "train_roundtrip_2ac_inr": 3100,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr)",
                "flight_roundtrip_inr": 5200
            },
            "hyderabad": {
                "train_available": True,
                "train_details": "Kacheguda Vasco Express (16 hrs)",
                "train_roundtrip_sleeper_inr": 1100,
                "train_roundtrip_3ac_inr": 2800,
                "train_roundtrip_2ac_inr": 4000,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 20 mins)",
                "flight_roundtrip_inr": 6200
            }
        },
        "daily_food_activities_estimate_inr": 1500
    },
    "manali": {
        "name": "Manali & Solang Valley (Himachal Pradesh)",
        "tagline": "Snow-Capped Peaks, Pine Forests & Adventure Sports",
        "category": "Hill Station & Adventure Hub",
        "best_time_to_visit": "October to June (Dec-Feb for Snow)",
        "key_attractions": [
            "Solang Valley (Skiing/Paragliding)", "Atal Tunnel & Sissu (Lahaul)",
            "Rohtang Pass", "Hadimba Temple", "Old Manali Cafes", "Jogini Waterfall Trek"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Backpacker Hostel",
                "name": "The Hosteller / Zostel Old Manali / Riverside Camps",
                "price_per_night_inr": 950,
                "rating": "4.3 ★",
                "amenities": "Mountain View Dorm / Cottage, Free Wi-Fi, Bonfire, Cafe, Trek Guides",
                "description": "Rustic, lively mountain stay with amazing valley views."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Comfort",
                "name": "Snow Valley Resorts / Apple Country Resort",
                "price_per_night_inr": 3200,
                "rating": "4.4 ★",
                "amenities": "Heated Rooms, Wooden Interiors, Panoramic Valley Balcony, Multi-Cuisine Buffet",
                "description": "Cozy family-friendly stay with spectacular Himalayan mountain views."
            },
            "premium": {
                "tier": "Premium 4-Star Mountain Resort",
                "name": "The Himalayan Resort & Spa / ManuAllaya Resort",
                "price_per_night_inr": 9200,
                "rating": "4.7 ★",
                "amenities": "Victorian Castle Architecture, Heated Pool, Mountain Spa, Fireplace, Bar",
                "description": "Luxury castle resort blending Victorian elegance with snow-clad views."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Glamping & Chalet",
                "name": "Span Resort & Spa / Larisa Resort Manali",
                "price_per_night_inr": 24000,
                "rating": "4.9 ★",
                "amenities": "Private Riverside Cottage, Heated Jacuzzi, Organic Orchard, Helipad, Luxury Spa",
                "description": "Exclusive riverside luxury nestled amidst walnut orchards and snow peaks."
            }
        },
        "transport_from": {
            "delhi": {
                "train_available": True,
                "train_details": "Vande Bharat to Chandigarh (3 hrs) + Volvo Bus/Cab to Manali (7 hrs)",
                "train_roundtrip_sleeper_inr": 1200,
                "train_roundtrip_3ac_inr": 2600,
                "train_roundtrip_2ac_inr": 3800,
                "flight_available": True,
                "flight_details": "Flight to Bhuntar/Kullu Airport (1 hr 15 mins) + 1 hr cab",
                "flight_roundtrip_inr": 9500
            },
            "mumbai": {
                "train_available": True,
                "train_details": "Mumbai Rajdhani to Delhi + Volvo to Manali (32 hrs total)",
                "train_roundtrip_sleeper_inr": 2400,
                "train_roundtrip_3ac_inr": 5400,
                "train_roundtrip_2ac_inr": 7800,
                "flight_available": True,
                "flight_details": "Flight Mumbai to Delhi/Chandigarh + Volvo/Cab to Manali",
                "flight_roundtrip_inr": 11500
            },
            "bengaluru": {
                "train_available": False,
                "train_details": "Train to Delhi (34 hrs) + Volvo Bus to Manali",
                "flight_available": True,
                "flight_details": "Flight to Chandigarh (3 hrs) + Volvo Bus/Cab to Manali",
                "flight_roundtrip_inr": 12500
            },
            "pune": {
                "train_available": False,
                "train_details": "Train to Delhi + Volvo to Manali",
                "flight_available": True,
                "flight_details": "Flight Pune to Chandigarh + Cab to Manali",
                "flight_roundtrip_inr": 11800
            }
        },
        "daily_food_activities_estimate_inr": 1200
    },
    "jaipur": {
        "name": "Jaipur & Udaipur (Rajasthan Royal Heritage)",
        "tagline": "Majestic Forts, Royal Palaces & Rich Rajasthani Culture",
        "category": "Heritage & Royal Tourism",
        "best_time_to_visit": "October to March",
        "key_attractions": [
            "Amer Fort & Light Show", "Hawa Mahal & City Palace", "Jantar Mantar",
            "Nahargarh Fort Sunset Point", "Chokhi Dhani Cultural Village", "Lake Pichola (Udaipur)"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Traditional Haveli Hostel",
                "name": "Moustache Jaipur / Zostel Jaipur / Traditional Haveli Guesthouse",
                "price_per_night_inr": 850,
                "rating": "4.3 ★",
                "amenities": "Heritage Courtyard, Rooftop Cafe overlooking Forts, AC Rooms, Folk Music",
                "description": "Authentic Rajasthani haveli experience at backpacker prices."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Heritage Hotel",
                "name": "Alsisar Haveli / Mandawa Haveli Jaipur",
                "price_per_night_inr": 3500,
                "rating": "4.5 ★",
                "amenities": "Carved Frescoes, Swimming Pool, Courtyard Dining, Traditional Puppet Shows",
                "description": "Restored 19th-century royal haveli with modern amenities."
            },
            "premium": {
                "tier": "Premium 4-Star Royal Palace Hotel",
                "name": "Samode Haveli / ITC Rajputana Luxury Collection",
                "price_per_night_inr": 10500,
                "rating": "4.7 ★",
                "amenities": "Royal Suites, Ayurvedic Spa, Grand Courtyards, Royal Rajasthani Thali Dining",
                "description": "Regal ambiance with maharaja hospitality and heritage luxury."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star World-Class Palace",
                "name": "Rambagh Palace (The Jewel of Jaipur) / Taj Lake Palace Udaipur",
                "price_per_night_inr": 42000,
                "rating": "5.0 ★",
                "amenities": "Living Palace Residence, Royal Carriage Welcome, Peacock Gardens, Private Butler, Jharokha Dining",
                "description": "Ranked #1 hotel in the world — stay where Kings and Queens once lived."
            }
        },
        "transport_from": {
            "delhi": {
                "train_available": True,
                "train_details": "Vande Bharat Express / Shatabdi Express (3.5 - 4.5 hrs)",
                "train_roundtrip_sleeper_inr": 500,
                "train_roundtrip_3ac_inr": 1400,
                "train_roundtrip_2ac_inr": 2100,
                "flight_available": True,
                "flight_details": "Direct Flight (55 mins)",
                "flight_roundtrip_inr": 4200
            },
            "mumbai": {
                "train_available": True,
                "train_details": "Jaipur Superfast Express (16-17 hrs)",
                "train_roundtrip_sleeper_inr": 1100,
                "train_roundtrip_3ac_inr": 2800,
                "train_roundtrip_2ac_inr": 4100,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 45 mins)",
                "flight_roundtrip_inr": 6500
            },
            "bengaluru": {
                "train_available": True,
                "train_details": "Mysuru Jaipur Express (40 hrs)",
                "train_roundtrip_sleeper_inr": 1800,
                "train_roundtrip_3ac_inr": 4600,
                "train_roundtrip_2ac_inr": 6800,
                "flight_available": True,
                "flight_details": "Direct Flight (2 hrs 30 mins)",
                "flight_roundtrip_inr": 8200
            },
            "ahmedabad": {
                "train_available": True,
                "train_details": "Vande Bharat Express / Ashram Express (7-9 hrs)",
                "train_roundtrip_sleeper_inr": 600,
                "train_roundtrip_3ac_inr": 1600,
                "train_roundtrip_2ac_inr": 2400,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr)",
                "flight_roundtrip_inr": 4800
            }
        },
        "daily_food_activities_estimate_inr": 1300
    },
    "kerala": {
        "name": "Kerala (Munnar Tea Hills & Alleppey Backwaters)",
        "tagline": "God's Own Country — Lush Tea Gardens, Houseboats & Ayurvedic Spas",
        "category": "Nature, Hills & Backwaters",
        "best_time_to_visit": "September to March",
        "key_attractions": [
            "Munnar Tea Gardens & Eravikulam National Park", "Alleppey Houseboat Cruise & Overnight Stay",
            "Mattupetty Dam", "Kathakali & Kalaripayattu Cultural Shows", "Fort Kochi & Chinese Fishing Nets"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Backpacker & Homestay",
                "name": "Zostel Munnar / Alleppey Backwater Homestays",
                "price_per_night_inr": 1100,
                "rating": "4.4 ★",
                "amenities": "Tea Garden Views, Free Wi-Fi, Authentic Homemade Kerala Meals, Village Canoe Rides",
                "description": "Warm, peaceful homestay amidst misty tea estates."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Comfort",
                "name": "Tea County Munnar / Lake Palace Backwater Resort",
                "price_per_night_inr": 4200,
                "rating": "4.5 ★",
                "amenities": "Spacious Balcony, Ayurvedic Massage Center, Valley Views, Multi-Cuisine Dining",
                "description": "Comfortable family resort surrounded by rolling green hills."
            },
            "premium": {
                "tier": "Premium 4-Star Resort / AC Deluxe Houseboat",
                "name": "Fragrant Nature Munnar / Traditional Private Luxury Houseboat (Alleppey)",
                "price_per_night_inr": 11500,
                "rating": "4.7 ★",
                "amenities": "Private Houseboat with Personal Chef & Captain, All Meals Included, Sunset Cruising",
                "description": "Floating luxury through scenic palm-fringed backwater lagoons."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Ayurvedic Wellness Resort",
                "name": "Kumarakom Lake Resort / Brunton Boatyard Kochi",
                "price_per_night_inr": 32000,
                "rating": "4.9 ★",
                "amenities": "Heritage Meandering Pool Villa, Royal Ayurvedic Treatments, Private Speedboat, Lakefront Dining",
                "description": "World-renowned luxury resort where Prince Charles celebrated his birthday."
            }
        },
        "transport_from": {
            "mumbai": {
                "train_available": True,
                "train_details": "Netravati Express / Mangala Lakshadweep Express to Kochi (24 hrs)",
                "train_roundtrip_sleeper_inr": 1500,
                "train_roundtrip_3ac_inr": 3800,
                "train_roundtrip_2ac_inr": 5600,
                "flight_available": True,
                "flight_details": "Direct Flight to Kochi (2 hrs)",
                "flight_roundtrip_inr": 6800
            },
            "delhi": {
                "train_available": True,
                "train_details": "Kerala Express to Kochi (40 hrs)",
                "train_roundtrip_sleeper_inr": 2100,
                "train_roundtrip_3ac_inr": 5200,
                "train_roundtrip_2ac_inr": 7600,
                "flight_available": True,
                "flight_details": "Direct Flight to Kochi (3 hrs 15 mins)",
                "flight_roundtrip_inr": 9200
            },
            "bengaluru": {
                "train_available": True,
                "train_details": "KSR Bengaluru Ernakulam Intercity / Vande Bharat (9 hrs)",
                "train_roundtrip_sleeper_inr": 700,
                "train_roundtrip_3ac_inr": 1800,
                "train_roundtrip_2ac_inr": 2600,
                "flight_available": True,
                "flight_details": "Direct Flight to Kochi (1 hr)",
                "flight_roundtrip_inr": 4200
            },
            "chennai": {
                "train_available": True,
                "train_details": "Chennai Alleppey Superfast / Vande Bharat (10 hrs)",
                "train_roundtrip_sleeper_inr": 750,
                "train_roundtrip_3ac_inr": 1900,
                "train_roundtrip_2ac_inr": 2800,
                "flight_available": True,
                "flight_details": "Direct Flight to Kochi (1 hr 15 mins)",
                "flight_roundtrip_inr": 4600
            }
        },
        "daily_food_activities_estimate_inr": 1400
    },
    "varanasi": {
        "name": "Varanasi (Kashi / Banaras)",
        "tagline": "The Spiritual Capital of India — Ghats, Ganga Aarti & Ancient Temples",
        "category": "Spiritual & Cultural Heritage",
        "best_time_to_visit": "October to March",
        "key_attractions": [
            "Grand Ganga Aarti at Dashashwamedh Ghat", "Kashi Vishwanath Temple Corridor",
            "Morning Sunrise Boat Ride on the Ganges", "Sarnath (Buddhist Heritage)",
            "Assi Ghat & Banarasi Silk Weaving Centers", "Banarasi Street Food Trail (Chaat, Lassi, Paan)"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Riverside Backpacker Hostel",
                "name": "Hostelavie Varanasi / Moustache Varanasi / Ghat Guesthouses",
                "price_per_night_inr": 750,
                "rating": "4.3 ★",
                "amenities": "Rooftop Yoga & Aarti Views, Free Wi-Fi, AC Dorm, Walking distance to Ghats",
                "description": "Vibrant backpacker hub located right along the historic riverfront ghats."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Heritage Comfort",
                "name": "Heritage Inn Varanasi / Hotel Surya Kaiser Palace",
                "price_per_night_inr": 2800,
                "rating": "4.4 ★",
                "amenities": "AC Deluxe Rooms, Garden Restaurant, Swimming Pool, Temple Transfer assistance",
                "description": "Comfortable heritage residence offering calm away from bustling alleys."
            },
            "premium": {
                "tier": "Premium 4-Star Palace Hotel",
                "name": "BrijRama Palace / Radisson Hotel Varanasi",
                "price_per_night_inr": 14500,
                "rating": "4.8 ★",
                "amenities": "18th-century Palace right on Darbhanga Ghat, Private Bajra Boat transfers, Classical Live Sitar, Fine Dining",
                "description": "Historic palace standing proudly over the holy Ganges since 1812."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Heritage Sanctuary",
                "name": "Taj Ganges Varanasi / Nadesar Palace",
                "price_per_night_inr": 35000,
                "rating": "4.9 ★",
                "amenities": "Historic Royal Palace with 40 Acres of Mango Orchards, Horse Carriage Tours, Royal Butler Service, Jiva Spa",
                "description": "Hosted Royalty and Dignitaries since 1835 in ultimate peaceful luxury."
            }
        },
        "transport_from": {
            "delhi": {
                "train_available": True,
                "train_details": "Vande Bharat Express / Kashi Vishwanath Express (8 hrs)",
                "train_roundtrip_sleeper_inr": 800,
                "train_roundtrip_3ac_inr": 2200,
                "train_roundtrip_2ac_inr": 3200,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 20 mins)",
                "flight_roundtrip_inr": 5500
            },
            "mumbai": {
                "train_available": True,
                "train_details": "Mahanagari Express / LTT Varanasi SF (25 hrs)",
                "train_roundtrip_sleeper_inr": 1400,
                "train_roundtrip_3ac_inr": 3600,
                "train_roundtrip_2ac_inr": 5200,
                "flight_available": True,
                "flight_details": "Direct Flight (2 hrs 10 mins)",
                "flight_roundtrip_inr": 7200
            },
            "kolkata": {
                "train_available": True,
                "train_details": "Vande Bharat Express / Poorva Express (7-10 hrs)",
                "train_roundtrip_sleeper_inr": 700,
                "train_roundtrip_3ac_inr": 1900,
                "train_roundtrip_2ac_inr": 2800,
                "flight_available": True,
                "flight_details": "Direct Flight (1 hr 15 mins)",
                "flight_roundtrip_inr": 4800
            },
            "bengaluru": {
                "train_available": True,
                "train_details": "Sanghamitra Express (42 hrs)",
                "train_roundtrip_sleeper_inr": 1900,
                "train_roundtrip_3ac_inr": 4800,
                "train_roundtrip_2ac_inr": 7000,
                "flight_available": True,
                "flight_details": "Direct Flight (2 hrs 30 mins)",
                "flight_roundtrip_inr": 7900
            }
        },
        "daily_food_activities_estimate_inr": 900
    },
    "andaman": {
        "name": "Andaman & Nicobar Islands (Port Blair & Havelock Island)",
        "tagline": "Turquoise Waters, White Sand Beaches & World-Class Scuba Diving",
        "category": "Tropical Island Paradise",
        "best_time_to_visit": "October to May",
        "key_attractions": [
            "Radhanagar Beach (Asia's Best Beach)", "Scuba Diving & Snorkeling at Elephant Beach",
            "Cellular Jail Light & Sound Show", "Ross Island Historic Ruins",
            "Catamaran Cruise (Makruzz) to Havelock & Neil Island", "Chidiya Tapu Sunset Point"
        ],
        "hotels": {
            "cheapest": {
                "tier": "Budget / Island Beach Hut & Homestay",
                "name": "Havelock Beach Eco Huts / Port Blair Guesthouses",
                "price_per_night_inr": 1400,
                "rating": "4.1 ★",
                "amenities": "Eco Bamboo Hut, Fan/AC, Attached Bath, 2 mins from Beach, Dive Shop Nearby",
                "description": "Laid-back island living for travelers who want beach proximity on a budget."
            },
            "comfort": {
                "tier": "Mid-Range / 3-Star Island Resort",
                "name": "Symphony Palms Beach Resort / SeaShell Port Blair",
                "price_per_night_inr": 4800,
                "rating": "4.4 ★",
                "amenities": "Wooden Cottages, Private Beach Access, Multi-Cuisine Seafood Restaurant, Bar",
                "description": "Charming wooden cottages under palm trees with direct ocean access."
            },
            "premium": {
                "tier": "Premium 4-Star Beachfront Resort",
                "name": "Barefoot at Havelock / Silver Sand Beach Resort",
                "price_per_night_inr": 12500,
                "rating": "4.7 ★",
                "amenities": "Nicobari Cottages in Rainforest, Direct Radhanagar Beach Access, PADI Scuba Center, Spa",
                "description": "Eco-luxury resort hidden in lush tropical rainforest opening onto white sands."
            },
            "richest": {
                "tier": "Ultra-Luxury 5-Star Private Island Villa",
                "name": "Taj Exotica Resort & Spa, Andamans",
                "price_per_night_inr": 38000,
                "rating": "4.9 ★",
                "amenities": "Sustainable Luxury Stilt Villa (1580 sq ft), Olympic Infinity Pool, Private Diving Yacht, Gourmet Dining",
                "description": "World-class 5-star island sanctuary set on 46 acres of Radhanagar Beach."
            }
        },
        "transport_from": {
            "chennai": {
                "train_available": False,
                "train_details": "No train connectivity (Island destination)",
                "flight_available": True,
                "flight_details": "Direct Flight to Port Blair (2 hrs 15 mins)",
                "flight_roundtrip_inr": 8500
            },
            "kolkata": {
                "train_available": False,
                "train_details": "No train connectivity (Island destination)",
                "flight_available": True,
                "flight_details": "Direct Flight to Port Blair (2 hrs 20 mins)",
                "flight_roundtrip_inr": 8200
            },
            "mumbai": {
                "train_available": False,
                "train_details": "No train connectivity (Island destination)",
                "flight_available": True,
                "flight_details": "Direct/Connecting Flight (3 hrs 30 mins)",
                "flight_roundtrip_inr": 12500
            },
            "delhi": {
                "train_available": False,
                "train_details": "No train connectivity (Island destination)",
                "flight_available": True,
                "flight_details": "Direct/Connecting Flight (3 hrs 45 mins)",
                "flight_roundtrip_inr": 13800
            },
            "bengaluru": {
                "train_available": False,
                "train_details": "No train connectivity (Island destination)",
                "flight_available": True,
                "flight_details": "Direct Flight to Port Blair (2 hrs 30 mins)",
                "flight_roundtrip_inr": 9800
            }
        },
        "daily_food_activities_estimate_inr": 1800
    }
}


def normalize_destination(name: str) -> Optional[str]:
    """Normalize user input destination name to database key."""
    n = name.strip().lower()
    if any(w in n for w in ["ujjain", "mahakal", "mahakaleshwar", "shipra", "bhasma aarti"]):
        return "ujjain"
    if any(w in n for w in ["kashmir", "srinagar", "gulmarg", "pahalgam", "dal lake", "sonamarg"]):
        return "kashmir"
    if any(w in n for w in ["manali", "solang", "himachal", "sissu", "rohtang", "kullu"]):
        return "manali"
    if any(w in n for w in ["goa", "baga", "calangute", "panaji"]):
        return "goa"
    if any(w in n for w in ["rajasthan", "jaipur", "udaipur", "jodhpur", "jaisalmer", "pink city"]):
        return "jaipur"
    if any(w in n for w in ["kerala", "munnar", "alleppey", "kochi", "cochin", "alappuzha"]):
        return "kerala"
    if any(w in n for w in ["varanasi", "banaras", "kashi"]):
        return "varanasi"
    if any(w in n for w in ["andaman", "nicobar", "port blair", "havelock", "radhanagar"]):
        return "andaman"
    return None



def normalize_source(name: str) -> str:
    """Normalize origin source city."""
    n = name.strip().lower()
    if "delhi" in n or "ncr" in n:
        return "delhi"
    if "bengaluru" in n or "bangalore" in n:
        return "bengaluru"
    if "pune" in n:
        return "pune"
    if "hyderabad" in n:
        return "hyderabad"
    if "chennai" in n:
        return "chennai"
    if "kolkata" in n or "calcutta" in n:
        return "kolkata"
    if "ahmedabad" in n:
        return "ahmedabad"
    return "mumbai"  # default origin


def get_holiday_package(
    destination: str,
    source_city: str = "Mumbai",
    duration_days: int = 3,
    hotel_tier: str = "all",
    num_travelers: int = 1
) -> Dict[str, Any]:
    """Calculate and return a comprehensive holiday package estimate.

    Args:
        destination: Holiday destination (e.g. 'Goa', 'Manali', 'Jaipur', 'Kerala', 'Varanasi', 'Andaman').
        source_city: Starting origin city (e.g. 'Mumbai', 'Delhi', 'Bengaluru', 'Pune', 'Kolkata', 'Chennai'). Default is 'Mumbai'.
        duration_days: Number of days for the vacation (e.g. 3, 4, 5, 7). Default is 3 days (2 nights).
        hotel_tier: Hotel budget tier ('cheapest', 'comfort', 'premium', 'richest', or 'all'). Default is 'all'.
        num_travelers: Number of people traveling. Default is 1.

    Returns:
        A dictionary containing destination details, return transport options, tiered hotel choices,
        and calculated total package prices (cheapest budget to richest luxury).
    """
    dest_key = normalize_destination(destination)
    if not dest_key:
        return {
            "status": "error",
            "message": f"Destination '{destination}' not found in our featured packages.",
            "available_destinations": ["Goa", "Manali", "Ujjain", "Kashmir", "Rajasthan / Jaipur", "Kerala", "Varanasi", "Andaman"]
        }

    # Try fetching from Supabase database first
    try:
        from supabase_db import fetch_holiday_packages_from_supabase
        supa_destinations = fetch_holiday_packages_from_supabase()
    except Exception:
        supa_destinations = {}

    db_source = supa_destinations if (supa_destinations and dest_key in supa_destinations) else DESTINATIONS_DATA
    dest = db_source[dest_key]
    source_key = normalize_source(source_city)

    # Transport details
    transport_info = dest.get("transport_from", {}).get(source_key)
    transport_notice = ""
    
    if not transport_info:
        # If the source city is not available, we STILL return the hotel package
        # but we mark transport as unavailable and add a clear notice.
        transport_notice = f"No available flights or trains from {source_city.title()}."
        
        transport_info = {
            "train_available": False,
            "flight_available": False
        }
    
    source_label = source_key.title()
    nights = max(1, duration_days - 1)
    travelers = max(1, num_travelers)
    rooms_needed = math.ceil(travelers / 2)  # 2 people per room assumption

    # Calculate packages for each hotel tier
    packages = []
    hotels = dest["hotels"]
    tiers_to_process = ["cheapest", "comfort", "premium", "richest"] if hotel_tier.lower() == "all" else [hotel_tier.lower()]

    for tier_key in tiers_to_process:
        if tier_key in hotels:
            h = hotels[tier_key]
            # Handle key mismatch between local dict and Supabase JSON
            price_per_night = h.get("price_per_night_inr") or h.get("price_per_night", 0)
            hotel_total = price_per_night * nights * rooms_needed
            food_activities_total = dest["daily_food_activities_estimate_inr"] * duration_days * travelers

            # 1. Budget package with Train (if available)
            if transport_info.get("train_available"):
                train_fare_per_person = transport_info.get("train_roundtrip_3ac_inr", 2000)
                total_with_train = (train_fare_per_person * travelers) + hotel_total + food_activities_total
            else:
                train_fare_per_person = None
                total_with_train = None

            # 2. Package with Flight
            if transport_info.get("flight_available"):
                flight_fare_per_person = transport_info.get("flight_roundtrip_inr", 6000)
                total_with_flight = (flight_fare_per_person * travelers) + hotel_total + food_activities_total
            else:
                flight_fare_per_person = None
                total_with_flight = None

            packages.append({
                "tier_key": tier_key,
                "tier_name": h["tier"],
                "hotel_name": h["name"],
                "hotel_price_per_night_inr": h["price_per_night_inr"],
                "hotel_total_inr": hotel_total,
                "rating": h["rating"],
                "amenities": h["amenities"],
                "description": h["description"],
                "estimated_food_activities_total_inr": food_activities_total,
                "package_total_with_train_inr": total_with_train,
                "package_total_with_flight_inr": total_with_flight
            })

    return {
        "status": "success",
        "destination": dest["name"],
        "tagline": dest["tagline"],
        "category": dest["category"],
        "best_time_to_visit": dest["best_time_to_visit"],
        "key_attractions": dest["key_attractions"],
        "source_city": source_label,
        "duration_days": duration_days,
        "duration_nights": nights,
        "travelers": travelers,
        "rooms": rooms_needed,
        "transport": {
            "source": source_label,
            "transport_notice": transport_notice,
            "train_available": transport_info.get("train_available", False),
            "train_details": transport_info.get("train_details", "N/A"),
            "train_roundtrip_sleeper_inr": transport_info.get("train_roundtrip_sleeper_inr"),
            "train_roundtrip_3ac_inr": transport_info.get("train_roundtrip_3ac_inr"),
            "train_roundtrip_2ac_inr": transport_info.get("train_roundtrip_2ac_inr"),
            "flight_available": transport_info.get("flight_available", False),
            "flight_details": transport_info.get("flight_details", "N/A"),
            "flight_roundtrip_inr": transport_info.get("flight_roundtrip_inr")
        },
        "packages": packages
    }
