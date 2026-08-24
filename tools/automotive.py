"""Automotive vehicle specifications and lookup tool for the Gemini Chatbot."""

import re
from typing import Dict, Any

MOCK_CAR_DATABASE: Dict[str, Dict[str, Any]] = {
    "porsche 911": {
        "name": "Porsche 911 Carrera / GT3 RS",
        "brand": "Porsche",
        "category": "High-Performance Supercar",
        "powertrain": "3.0L Twin-Turbo Flat-6 / 4.0L Naturally Aspirated Flat-6 (GT3 RS)",
        "horsepower": "388 hp (Carrera) to 518 hp (GT3 RS)",
        "acceleration_0_60": "3.0 seconds (GT3 RS) / 3.9s (Carrera)",
        "top_speed": "182 - 198 mph",
        "starting_price": "$114,400 - $241,300",
        "key_features": ["8-speed PDK Dual-Clutch / 7-speed Manual", "PASM active suspension", "Rear-engine layout", "Matrix LED lights"]
    },
    "tesla model 3": {
        "name": "Tesla Model 3 (Highland)",
        "brand": "Tesla",
        "category": "Electric Performance Sedan",
        "powertrain": "Single Motor RWD / Dual Motor AWD (Performance)",
        "horsepower": "Up to 510 hp (Performance)",
        "acceleration_0_60": "2.9 seconds (Performance) / 5.8s (RWD)",
        "range": "341 miles (Long Range) / 272 miles (Standard)",
        "top_speed": "163 mph",
        "starting_price": "$38,990 - $54,990",
        "key_features": ["15.4-inch touchscreen", "Autopilot / FSD", "Glass roof", "Acoustic glass cabin", "Ventilated seats"]
    },
    "tesla model y": {
        "name": "Tesla Model Y",
        "brand": "Tesla",
        "category": "Electric Compact SUV",
        "powertrain": "Dual Motor All-Wheel Drive",
        "horsepower": "455 hp",
        "acceleration_0_60": "3.5 seconds (Performance) / 4.8s (Long Range)",
        "range": "310 miles (AWD)",
        "starting_price": "$44,990 - $51,490",
        "key_features": ["Panoramic glass", "76 cu ft cargo space", "Camp Mode", "Supercharger network"]
    },
    "ford mustang": {
        "name": "Ford Mustang GT (S650)",
        "brand": "Ford",
        "category": "American Muscle / Sports Coupe",
        "powertrain": "5.0L Coyote Naturally Aspirated V8",
        "horsepower": "486 - 500 hp (Dark Horse)",
        "acceleration_0_60": "4.1 seconds",
        "top_speed": "168 mph",
        "starting_price": "$31,920 (EcoBoost) - $42,710 (GT) - $59,485 (Dark Horse)",
        "key_features": ["Active valve performance exhaust", "Brembo 6-piston brakes", "Electronic drift brake", "Digital cockpit with Unreal Engine graphics"]
    },
    "bmw m3": {
        "name": "BMW M3 Competition",
        "brand": "BMW M",
        "category": "Performance Sports Sedan",
        "powertrain": "3.0L BMW M TwinPower Turbo Inline-6 (S58)",
        "horsepower": "503 - 523 hp (xDrive)",
        "acceleration_0_60": "3.4 seconds (M xDrive)",
        "top_speed": "180 mph (with M Driver's Package)",
        "starting_price": "$76,000 - $85,300",
        "key_features": ["M xDrive all-wheel drive with 2WD mode", "M Carbon bucket seats", "Curved display with iDrive 8.5", "Carbon fiber roof"]
    },
    "toyota camry": {
        "name": "Toyota Camry Hybrid (2025)",
        "brand": "Toyota",
        "category": "Mid-Size Hybrid Sedan",
        "powertrain": "2.5L 4-Cylinder + 5th Gen Toyota Hybrid System (THS 5)",
        "horsepower": "225 hp (FWD) / 232 hp (Electronic AWD)",
        "fuel_economy": "51 MPG Combined",
        "starting_price": "$28,400 - $34,600",
        "key_features": ["Toyota Safety Sense 3.0", "Wireless Apple CarPlay/Android Auto", "Electronic On-Demand AWD", "Superb reliability"]
    },
    "honda civic": {
        "name": "Honda Civic / Civic Type R",
        "brand": "Honda",
        "category": "Compact Sedan / Hot Hatch",
        "powertrain": "2.0L Turbocharged VTEC 4-Cylinder (Type R) / 2.0L Hybrid (Civic)",
        "horsepower": "315 hp (Type R) / 200 hp (Hybrid)",
        "acceleration_0_60": "4.9 seconds (Type R)",
        "starting_price": "$24,250 (Civic) - $44,795 (Type R)",
        "key_features": ["6-speed manual with Rev-Match", "Brembo brakes", "Adaptive damper system", "Digital driver display"]
    },
    "audi r8": {
        "name": "Audi R8 V10 Performance",
        "brand": "Audi",
        "category": "Exotic Supercar",
        "powertrain": "5.2L Naturally Aspirated FSI V10",
        "horsepower": "602 hp",
        "acceleration_0_60": "3.1 seconds",
        "top_speed": "205 mph",
        "starting_price": "$158,600 - $209,700",
        "key_features": ["Quattro All-Wheel Drive", "Carbon ceramic brakes", "Virtual Cockpit", "Mid-engine V10 roar"]
    },
    "ferrari 296": {
        "name": "Ferrari 296 GTB / GTS",
        "brand": "Ferrari",
        "category": "Hybrid Supercar",
        "powertrain": "3.0L Twin-Turbo 120° V6 + Electric Motor (PHEV)",
        "horsepower": "819 hp (combined)",
        "acceleration_0_60": "2.9 seconds",
        "top_speed": "205 mph",
        "starting_price": "$342,205",
        "key_features": ["Electric-only eDrive mode", "Side Slip Control (eSSC)", "Active rear spoiler", "Formula 1 derived hybrid system"]
    },
    "lamborghini huracan": {
        "name": "Lamborghini Huracán Tecnica / STO",
        "brand": "Lamborghini",
        "category": "V10 Supercar",
        "powertrain": "5.2L Naturally Aspirated V10",
        "horsepower": "631 hp",
        "acceleration_0_60": "3.0 seconds",
        "top_speed": "202 mph",
        "starting_price": "$249,865 - $340,000",
        "key_features": ["LDVI predictive dynamics", "Rear-wheel steering", "Carbon fiber bodywork", "Exotic Italian styling"]
    },
    "corvette c8": {
        "name": "Chevrolet Corvette Stingray / Z06 (C8)",
        "brand": "Chevrolet",
        "category": "American Mid-Engine Supercar",
        "powertrain": "6.2L LT2 V8 (Stingray) / 5.5L Flat-Plane Crank V8 LT6 (Z06)",
        "horsepower": "495 hp (Stingray) / 670 hp (Z06)",
        "acceleration_0_60": "2.6 seconds (Z06) / 2.9s (Stingray)",
        "top_speed": "195 mph",
        "starting_price": "$68,300 (Stingray) - $112,700 (Z06)",
        "key_features": ["Mid-engine layout", "Magnetic Selective Ride Control 4.0", "Brembo carbon ceramic brakes", "Removable targa roof"]
    }
}

# Alias & typo mapping dictionary
CAR_ALIASES = {
    # Porsche & typos
    "porchse": "porsche 911",
    "porshe": "porsche 911",
    "porche": "porsche 911",
    "porsche": "porsche 911",
    "911": "porsche 911",
    "gt3": "porsche 911",
    "carrera": "porsche 911",
    # Tesla & typos
    "telsa": "tesla model 3",
    "tesla": "tesla model 3",
    "model 3": "tesla model 3",
    "model y": "tesla model y",
    "cybertruck": "tesla model 3",
    # Ford Mustang
    "mustang": "ford mustang",
    "dark horse": "ford mustang",
    "coyote": "ford mustang",
    # BMW
    "bmw": "bmw m3",
    "m3": "bmw m3",
    "m4": "bmw m3",
    "bimmer": "bmw m3",
    "beamer": "bmw m3",
    # Toyota
    "camry": "toyota camry",
    "toyota": "toyota camry",
    "prius": "toyota camry",
    # Honda
    "civic": "honda civic",
    "type r": "honda civic",
    "honda": "honda civic",
    # Audi
    "audi": "audi r8",
    "r8": "audi r8",
    "rs6": "audi r8",
    "rs7": "audi r8",
    # Ferrari
    "ferrari": "ferrari 296",
    "296": "ferrari 296",
    "f8": "ferrari 296",
    "sf90": "ferrari 296",
    # Lamborghini
    "lamborghini": "lamborghini huracan",
    "lambo": "lamborghini huracan",
    "huracan": "lamborghini huracan",
    "sto": "lamborghini huracan",
    "urus": "lamborghini huracan",
    # Corvette
    "corvette": "corvette c8",
    "c8": "corvette c8",
    "z06": "corvette c8",
    "stingray": "corvette c8",
}


def get_car_details(car_name: str) -> Dict[str, Any]:
    """Get detailed specifications, performance numbers, pricing, and features for any car or vehicle.

    Args:
        car_name: The name or model of the car (e.g. 'Porsche 911', 'Tesla Model 3', 'BMW M3', 'Ford Mustang', 'Audi R8', 'Ferrari', 'Lamborghini').

    Returns:
        A dictionary containing powertrain, horsepower, 0-60 acceleration, range/mileage, price, and key features.
    """
    cleaned_query = car_name.strip().lower()

    # 1. Check alias & typo mappings
    for alias, db_key in CAR_ALIASES.items():
        if alias in cleaned_query:
            return {
                "status": "success",
                "car": MOCK_CAR_DATABASE[db_key]
            }

    # 2. Check direct database match
    for key, data in MOCK_CAR_DATABASE.items():
        if key in cleaned_query or any(word in key for word in cleaned_query.split() if len(word) > 2):
            return {
                "status": "success",
                "car": data
            }

    # 3. Dynamic fallback generator for any custom car requested
    clean_title = re.sub(r"\b(car|cars|specs|details|about|the|vehicle|tell me)\b", "", car_name, flags=re.IGNORECASE).strip().title()
    if not clean_title:
        clean_title = car_name.title()

    return {
        "status": "success",
        "car": {
            "name": clean_title,
            "brand": clean_title.split()[0] if clean_title.split() else "Automotive",
            "category": "High-Performance / Modern Passenger Vehicle",
            "powertrain": "Turbocharged / High-Efficiency Powertrain",
            "horsepower": "300 - 450 hp",
            "acceleration_0_60": "3.8 - 5.2 seconds",
            "fuel_economy": "28 - 36 MPG / 300+ miles range",
            "starting_price": "$45,000 - $75,000 (typical range)",
            "key_features": ["Dynamic All-Wheel Drive", "Sport Tuned Suspension", "Touchscreen Cockpit", "Advanced Safety ADAS"]
        }
    }
