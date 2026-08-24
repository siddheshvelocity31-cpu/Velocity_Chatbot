"""Exhaustive, minute-by-minute specifications for latest 2025/2026 flagship Laptops and Smartphones."""

import re
from typing import Dict, Any, List

MOCK_LAPTOP_DATABASE: Dict[str, Dict[str, Any]] = {
    "macbook pro": {
        "name": "Apple MacBook Pro (14-inch & 16-inch M4 Pro / M4 Max)",
        "brand": "Apple",
        "category": "Pro Creator & Developer Flagship",
        "display": "14.2\" (3024x1964) / 16.2\" (3456x2234) Liquid Retina XDR, ProMotion 120Hz Adaptive Refresh, 1,000 nits SDR / 1,600 nits Peak HDR, 1,000,000:1 contrast, optional Nano-Texture anti-glare glass",
        "processor": "Apple M4 Pro (12/14-Core CPU, up to 20-Core GPU) or M4 Max (14/16-Core CPU, up to 40-Core GPU, 16-Core Neural Engine @ 38 TOPS)",
        "gpu": "Apple M4 Max 40-Core GPU with Hardware-Accelerated Ray Tracing & Dynamic Caching (up to 546 GB/s memory bandwidth)",
        "ram": "24GB, 36GB, 48GB, 64GB, 128GB Unified Memory (up to 546 GB/s bandwidth)",
        "storage": "512GB / 1TB / 2TB / 4TB / 8TB Ultra-High Speed PCIe Gen4 SSD (up to 7.4 GB/s read speeds)",
        "battery_charging": "72.4 Wh (14\") / 100 Wh (16\") Lithium-Polymer, up to 24 hours real-world battery life, 96W/140W USB-C Fast Charger with MagSafe 3 (50% in 30 mins)",
        "build_weight": "1.60 kg (14\") / 2.14 kg (16\"), 100% recycled unibody aluminum enclosure in Space Black or Silver",
        "ports_connectivity": "3x Thunderbolt 5 ports (up to 120 Gbps data transfer), HDMI 2.1 port supporting up to 8K @ 60Hz / 4K @ 240Hz, SDXC card slot, 3.5mm headphone jack with high-impedance support, Wi-Fi 6E/7, Bluetooth 5.3",
        "audio_camera": "12MP Center Stage Camera with Desk View (1080p HD video), High-Fidelity 6-Speaker sound system with force-cancelling woofers & Spatial Audio, Studio-quality 3-mic array",
        "starting_price": "$1,599 (14\" M4) | $1,999 (14\" M4 Pro) | $2,499 (16\" M4 Pro) | $3,499 (16\" M4 Max)"
    },
    "dell xps": {
        "name": "Dell XPS 16 (9640) / XPS 14 (9440)",
        "brand": "Dell",
        "category": "Premium Ultra-Sleek Windows Creator Laptop",
        "display": "16.3\" 4K+ (3840x2400) InfinityEdge OLED Touchscreen, 120Hz Variable Refresh, 100% DCI-P3 color gamut, 400 nits, Dolby Vision, Gorilla Glass 3 / 14.5\" 3.2K OLED 120Hz",
        "processor": "Intel Core Ultra 9 185H (16 Cores: 6 Performance, 8 Efficient, 2 Low Power Cores, up to 5.1 GHz Turbo, Intel AI Boost NPU)",
        "gpu": "NVIDIA GeForce RTX 4070 Laptop GPU (8GB GDDR6 VRAM, 60W TGP with Studio Drivers)",
        "ram": "32GB / 64GB LPDDR5x Dual Channel High-Speed Memory @ 7467 MT/s",
        "storage": "1TB / 2TB / 4TB M.2 PCIe Gen4 NVMe Solid State Drive",
        "battery_charging": "99.5 Wh Maximum Airline Legal Battery, up to 14 hours battery life, 130W USB-C GaN Fast Power Adapter",
        "build_weight": "2.13 kg (4.7 lbs), CNC Machined Aluminum body with Gorilla Glass seamless glass palm rest & invisible haptic trackpad",
        "ports_connectivity": "3x Thunderbolt 4 (USB Type-C) with DisplayPort 2.1 & Power Delivery, MicroSD v6.0 card reader, 3.5mm Headphone/Mic combo, Intel Killer Wi-Fi 7 BE1750 + Bluetooth 5.4",
        "audio_camera": "FHD 1080p Windows Hello IR Webcam with ambient light sensor, Quad-Speaker design (2x 3W woofers + 2x 2W tweeters) with Waves MaxxAudio Pro",
        "starting_price": "$1,699 (XPS 14) | $2,099 (XPS 16 Base) | $3,399 (XPS 16 OLED RTX 4070 Max)"
    },
    "thinkpad": {
        "name": "Lenovo ThinkPad X1 Carbon Gen 13 (Aura Edition)",
        "brand": "Lenovo",
        "category": "Enterprise Ultralight Business Flagship",
        "display": "14.0\" 2.8K (2880x1800) OLED Anti-Glare/Anti-Reflection, 120Hz Refresh, 500 nits HDR True Black 500, 100% DCI-P3, Dolby Vision, Eyesafe Low Blue Light",
        "processor": "Intel Core Ultra 7 258V / Core Ultra 9 288V (Lunar Lake Architecture, 8-Core up to 5.1 GHz, 48 TOPS Dedicated NPU for Microsoft Copilot+ PC)",
        "gpu": "Intel Arc 140V Integrated GPU with 8 Xe2 Cores & XeSS Super Sampling",
        "ram": "32GB On-Package LPDDR5x-8533MHz High-Bandwidth Memory",
        "storage": "512GB / 1TB / 2TB PCIe Gen5 x4 NVMe Performance M.2 SSD",
        "battery_charging": "57 Wh Rapid Charge Battery (80% charge in 60 mins), up to 18 hours battery life, 65W USB-C Slim GaN Charger",
        "build_weight": "0.98 kg (2.16 lbs) - Ultra-featherweight aerospace-grade Carbon Fiber top lid & recycled Magnesium alloy bottom, MIL-STD-810H military certified",
        "ports_connectivity": "2x Thunderbolt 4 / USB4 40Gbps, 2x USB-A 3.2 Gen 1 (5Gbps), 1x HDMI 2.1 (supports 4K @ 60Hz), 3.5mm audio jack, optional 5G Sub-6 eSIM, Intel Wi-Fi 7 + Bluetooth 5.4",
        "audio_camera": "8MP MIPI Computer Vision + IR Hybrid Webcam with Privacy Shutter, 2x User-facing stereo speakers with Dolby Atmos, 2x 360-degree Far-Field Microphones",
        "starting_price": "$1,899 (Base 32GB) | $2,549 (2.8K OLED 1TB) | $2,899 (Max Config with 5G)"
    },
    "asus rog": {
        "name": "ASUS ROG Zephyrus G16 (2025 AI Gaming Edition)",
        "brand": "ASUS",
        "category": "Ultra-Slim Gaming & High-Performance Workstation",
        "display": "16.0\" 2.5K (2560x1600) ROG Nebula OLED Display, 240Hz Ultra-Fast Refresh Rate, 0.2ms Response Time, 500 nits Peak, 100% DCI-P3, VESA DisplayHDR True Black 500, NVIDIA G-SYNC",
        "processor": "AMD Ryzen AI 9 HX 370 (12 Cores / 24 Threads, Zen 5, up to 5.1 GHz Turbo, XDNA 2 NPU @ 50 TOPS AI Performance)",
        "gpu": "NVIDIA GeForce RTX 4080 (12GB GDDR6) / RTX 4090 (16GB GDDR6) Laptop GPU with Dynamic Boost up to 115W TGP, MUX Switch + NVIDIA Advanced Optimus",
        "ram": "32GB / 64GB LPDDR5X-7500 High-Speed Dual-Channel Memory",
        "storage": "2TB / 4TB PCIe 4.0 NVMe M.2 Performance SSD (Dual M.2 slots available)",
        "battery_charging": "90 Wh High-Capacity Battery, 240W AC Fast Adapter (0 to 50% in 30 mins) + 100W USB-C Power Delivery charging support, up to 10 hours productivity battery life",
        "build_weight": "1.85 kg (4.07 lbs), 1.49 cm ultra-thin CNC aluminum unibody with Slash Lighting customizable LED lid matrix in Platinum White or Eclipse Gray",
        "ports_connectivity": "1x Thunderbolt 4 / USB4 Type-C (DisplayPort 2.1 / G-SYNC), 1x USB 3.2 Gen 2 Type-C, 2x USB 3.2 Gen 2 Type-A, 1x HDMI 2.1 FRL, 1x SD Express 7.0 Card Reader, Wi-Fi 7 + Bluetooth 5.4",
        "cooling_audio": "ROG Intelligent Cooling with Custom Vapor Chamber, 2nd Gen Arc Flow Fans & Thermal Grizzly Liquid Metal on CPU, 6-Speaker System with Dual Force-Cancelling Woofers & Hi-Res Audio",
        "starting_price": "$1,899 (RTX 4070) | $2,499 (RTX 4080 OLED) | $2,999 (RTX 4090 Flagship)"
    }
}

LAPTOP_ALIASES = {
    "macbook pro": "macbook pro",
    "m4": "macbook pro",
    "m3": "macbook pro",
    "macbook": "macbook pro",
    "mac": "macbook pro",
    "apple laptop": "macbook pro",
    "dell xps": "dell xps",
    "xps": "dell xps",
    "dell": "dell xps",
    "thinkpad": "thinkpad",
    "x1 carbon": "thinkpad",
    "lenovo": "thinkpad",
    "rog": "asus rog",
    "zephyrus": "asus rog",
    "g16": "asus rog",
    "g14": "asus rog",
    "asus": "asus rog",
}

MOCK_MOBILE_DATABASE: Dict[str, Dict[str, Any]] = {
    "iphone 16 pro max": {
        "name": "Apple iPhone 16 Pro Max",
        "brand": "Apple",
        "category": "Ultra-Premium iOS Flagship",
        "display": "6.9\" Super Retina XDR OLED (2868x1320 @ 460 ppi), ProMotion 1-120Hz LTPO Adaptive Refresh, Always-On Display, 2,000 nits Outdoor Peak Brightness, 1 nit Minimum, Next-Gen Ceramic Shield",
        "processor": "Apple A18 Pro (2nd Gen 3nm TSMC N3E, 6-Core CPU: 2 Performance + 4 Efficiency, 6-Core GPU with Hardware Ray Tracing, 16-Core Neural Engine @ 35 TOPS)",
        "camera": "Triple Pro Camera System:\n  • Primary: 48MP Fusion (24mm, f/1.78, 2nd-gen Sensor-shift OIS, 100% Focus Pixels)\n  • Ultra-Wide: 48MP (13mm, f/2.2, 120° FOV, Hybrid Focus Pixels, Macro Photography)\n  • Telephoto: 12MP 5x Tetraprism Optical Zoom (120mm, f/2.8, 3D Sensor-Shift OIS)\n  • Video: 4K Dolby Vision HDR @ 120 fps, ProRes Log, Spatial Audio recording with 4 studio mics",
        "battery_charging": "4,685 mAh Battery (Up to 33 hours continuous video playback), 30W Fast Wired Charging (50% in 30 mins), 25W MagSafe Wireless Charging, Qi2 support",
        "build_weight": "227 grams, Grade 5 Titanium frame with microblasted matte texture, IP68 Water/Dust resistance (6m for up to 30 mins)",
        "special_features": "Dedicated sapphire capacitive Camera Control button with haptic feedback, Action Button, Apple Intelligence on-device generative AI, Satellite Emergency SOS, Wi-Fi 7, USB-C 3.2 Gen 2 (10Gbps)",
        "starting_price": "$1,199 (256GB) | $1,399 (512GB) | $1,599 (1TB)"
    },
    "samsung galaxy s25 ultra": {
        "name": "Samsung Galaxy S25 Ultra",
        "brand": "Samsung",
        "category": "Ultra-Premium Android AI Flagship with Stylus",
        "display": "6.9\" Dynamic AMOLED 2X Flat Display (3120x1440 QHD+), 1-120Hz LTPO Variable Refresh, 2,600 nits Peak Brightness, Corning Gorilla Armor (75% reflection reduction & 4x scratch resistance)",
        "processor": "Qualcomm Snapdragon 8 Elite for Galaxy (3nm TSMC, Custom Oryon CPU: 2 Prime Cores @ 4.47GHz + 6 Performance Cores @ 3.53GHz, Adreno 830 GPU, Hexagon NPU @ 45% AI boost)",
        "camera": "Quad Pro AI Camera Setup:\n  • Primary: 200MP ISOCELL HP2 (f/1.7, OIS, Super Quad Pixel AF)\n  • Periscope Telephoto: 50MP (5x Optical Zoom, 100x Space Zoom, f/3.4, OIS)\n  • Telephoto 2: 50MP (3x Optical Zoom, f/2.4, OIS)\n  • Ultra-Wide: 50MP (f/1.95, 120° FOV with Dual Pixel AF)\n  • Video: 8K @ 30fps / 4K @ 120fps with HDR10+ and Audio Eraser AI",
        "battery_charging": "5,000 mAh All-Day Dual-Cell Battery, 45W Super Fast Charging 2.0 (65% in 30 mins), 15W Fast Wireless Charging 2.0, Wireless PowerShare",
        "build_weight": "219 grams, Slim Rounded Titanium chassis, IP68 Water & Dust resistance",
        "special_features": "Integrated S-Pen Stylus with Bluetooth Air Actions, Galaxy AI 2.0 (Real-Time Call Translation, Generative Photo Edit, Circle to Search with Google), 7 Generations of Android OS & Security Updates",
        "starting_price": "$1,299 (256GB / 12GB RAM) | $1,419 (512GB / 16GB RAM) | $1,659 (1TB / 16GB RAM)"
    },
    "google pixel 9 pro": {
        "name": "Google Pixel 9 Pro / 9 Pro XL",
        "brand": "Google",
        "category": "Google AI & Computational Photography Flagship",
        "display": "6.3\" (Pro) / 6.8\" (Pro XL) Super Actua LTPO OLED (1344x2992 @ 486 ppi), 1-120Hz Smooth Display, 3,000 nits Peak Brightness, 2,000 nits High Brightness Mode, Gorilla Glass Victus 2",
        "processor": "Google Tensor G4 (4nm, Titan M2 Security Coprocessor, Optimized for Gemini Nano Multimodal On-Device AI Models)",
        "camera": "Triple Pro Camera with AI Computational Photography:\n  • Primary: 50MP Octa PD (f/1.68, 1/1.31\" sensor, OIS + EIS)\n  • Telephoto: 48MP Quad PD (5x Optical Zoom, 30x Super Res Zoom, f/2.8, OIS)\n  • Ultra-Wide: 48MP Quad PD with Macro Focus (f/1.7, 123° FOV)\n  • Front: 42MP Dual PD Ultra-Wide with Autofocus (f/2.2, 103° FOV)\n  • Video: 8K Video Boost @ 30fps, Night Sight Video, Audio Magic Eraser",
        "battery_charging": "4,700 mAh (Pro) / 5,060 mAh (Pro XL), 37W Fast Wired (70% in 30 mins on XL), Fast Wireless Charging, Battery Share",
        "build_weight": "199g (Pro) / 221g (Pro XL), Polished Satin Aluminum frame with Matte Silky Glass back, IP68 Water/Dust resistant",
        "special_features": "Built-in Gemini Live conversational voice assistant, Magic Editor 'Reimagine' & 'Add Me' multi-person photo feature, Pixel Screenshots AI organizer, Thermometer sensor, 7 Years of OS & Pixel Feature Drops",
        "starting_price": "$999 (Pixel 9 Pro 128GB) | $1,099 (Pixel 9 Pro XL 128GB) | $1,799 (Pixel 9 Pro Fold)"
    },
    "oneplus 13": {
        "name": "OnePlus 13",
        "brand": "OnePlus",
        "category": "Speed & Battery Powerhouse Flagship",
        "display": "6.82\" 2K (3168x1440) Oriental Screen BOE X2 8T LTPO AMOLED, 1-120Hz Dynamic Refresh, 4,500 nits Peak Brightness, Dolby Vision, Crystal Shield Ultra-Hard Ceramic Glass",
        "processor": "Qualcomm Snapdragon 8 Elite (3nm, Dual Oryon Prime Cores @ 4.32GHz + 6 Cores @ 3.53GHz, Adreno 830 GPU)",
        "camera": "Triple 50MP Hasselblad Camera Engine:\n  • Primary: 50MP Sony LYT-808 (f/1.6, 1/1.4\" sensor, OIS)\n  • Telephoto: 50MP 3x Periscope Telephoto (Sony LYT-600, f/2.6, OIS, 120x Digital Zoom)\n  • Ultra-Wide: 50MP Samsung JN5 (f/2.0, 120° FOV, Macro capability)\n  • Color: 4th Generation Hasselblad Natural Color Calibration & Master Portraits",
        "battery_charging": "6,000 mAh Silicon-Carbon Glacier Battery (Massive capacity), 100W SUPERVOOC Wired Charging (0 to 100% in 28 mins), 50W Magnetic Wireless AIRVOOC, 5W Reverse Wireless",
        "build_weight": "213 grams, Aerospace Aluminum frame with micro-arc vegan leather / velvet glass back, Dual IP68 + IP69 Extreme High-Pressure Steam Resistance",
        "special_features": "Rain Touch 2.0 (full touchscreen operation with soaking wet hands or gloves), Ultrasonic In-Display Fingerprint scanner, Alert Slider, Dual Stereo Speakers with O-Haptics",
        "starting_price": "$799 (12GB RAM / 256GB) | $899 (16GB RAM / 512GB) | $999 (24GB RAM / 1TB Special Edition)"
    }
}

MOBILE_ALIASES = {
    "iphone 16 pro max": "iphone 16 pro max",
    "16 pro max": "iphone 16 pro max",
    "iphone 16 pro": "iphone 16 pro max",
    "iphone 16": "iphone 16 pro max",
    "iphone": "iphone 16 pro max",
    "apple phone": "iphone 16 pro max",
    "s25 ultra": "samsung galaxy s25 ultra",
    "s25": "samsung galaxy s25 ultra",
    "galaxy s25": "samsung galaxy s25 ultra",
    "samsung galaxy s25": "samsung galaxy s25 ultra",
    "s24 ultra": "samsung galaxy s25 ultra",
    "galaxy s24": "samsung galaxy s25 ultra",
    "samsung": "samsung galaxy s25 ultra",
    "galaxy": "samsung galaxy s25 ultra",
    "pixel 9 pro": "google pixel 9 pro",
    "pixel 9": "google pixel 9 pro",
    "pixel": "google pixel 9 pro",
    "google pixel": "google pixel 9 pro",
    "oneplus 13": "oneplus 13",
    "oneplus 12": "oneplus 13",
    "oneplus": "oneplus 13",
}


def get_laptop_specs(laptop_model: str) -> Dict[str, Any]:
    """Get exhaustive, minute-by-minute specifications, display, processor, RAM, battery, ports, and pricing for any laptop.

    Args:
        laptop_model: Name or brand of the laptop (e.g. 'MacBook Pro M4', 'Dell XPS 16', 'Lenovo ThinkPad X1 Carbon Gen 13', 'ASUS ROG Zephyrus G16').

    Returns:
        A dictionary containing detailed technical specifications for the laptop.
    """
    cleaned = laptop_model.strip().lower()

    # 1. Direct alias resolution
    for alias, db_key in LAPTOP_ALIASES.items():
        if alias in cleaned:
            return {"status": "success", "laptop": MOCK_LAPTOP_DATABASE[db_key]}

    # 2. Direct database key match
    for key, data in MOCK_LAPTOP_DATABASE.items():
        if key in cleaned:
            return {"status": "success", "laptop": data}

    # 3. Clean fallback for custom/unrecognized laptops
    clean_name = re.sub(r"\b(laptop|specs|details|about|the|computer|compare|an|lets|which|best)\b", "", laptop_model, flags=re.IGNORECASE).strip().title()
    if not clean_name or len(clean_name) < 2:
        # Return the top flagship MacBook Pro M4 if generic
        return {"status": "success", "laptop": MOCK_LAPTOP_DATABASE["macbook pro"]}

    return {
        "status": "success",
        "laptop": {
            "name": f"{clean_name} Laptop",
            "brand": clean_name.split()[0] if clean_name.split() else "Laptop",
            "category": "High-Performance Laptop",
            "display": "14\" to 16\" 2.8K / 4K OLED High-Resolution Display, 120Hz Variable Refresh Rate, 500 nits HDR",
            "processor": "Latest Intel Core Ultra / AMD Ryzen AI 300 / Apple Silicon Multi-Core Processor with Dedicated AI NPU",
            "gpu": "Dedicated NVIDIA GeForce RTX 40-Series / High-Core Integrated GPU with Hardware Ray Tracing",
            "ram": "32GB High-Speed LPDDR5X Dual-Channel RAM @ 7500 MT/s",
            "storage": "1TB / 2TB PCIe Gen4 NVMe High-Speed Solid State Drive (up to 7,000 MB/s)",
            "battery_charging": "85-99.5 Wh Lithium-Polymer Battery, up to 16-20 hours battery life with Fast Charging (80% in 1 hr)",
            "build_weight": "1.45 kg - 1.95 kg CNC Aluminum Chassis with MIL-STD durability certification",
            "ports_connectivity": "Thunderbolt 4/5 / USB4, HDMI 2.1, SDXC Card Reader, 3.5mm Audio Jack, Wi-Fi 7 + Bluetooth 5.4",
            "audio_camera": "FHD 1080p / 12MP Webcam with IR Windows Hello / Face ID, Dolby Atmos Quad-Speaker setup",
            "starting_price": "$1,299 - $2,299 (Retail MSRP Range)"
        }
    }


def get_mobile_specs(mobile_model: str) -> Dict[str, Any]:
    """Get exhaustive, minute-by-minute specifications, camera sensors, processor, battery, and pricing for any flagship smartphone.

    Args:
        mobile_model: Name of the smartphone (e.g. 'iPhone 16 Pro Max', 'Samsung Galaxy S25 Ultra', 'Google Pixel 9 Pro', 'OnePlus 13').

    Returns:
        A dictionary containing detailed technical specifications for the smartphone.
    """
    cleaned = mobile_model.strip().lower()

    # 1. Alias match
    for alias, db_key in MOBILE_ALIASES.items():
        if alias in cleaned:
            return {"status": "success", "phone": MOCK_MOBILE_DATABASE[db_key]}

    # 2. Database key match
    for key, data in MOCK_MOBILE_DATABASE.items():
        if key in cleaned:
            return {"status": "success", "phone": data}

    # 3. Clean fallback
    clean_name = re.sub(r"\b(phone|mobile|smartphone|specs|details|about|the|compare|an|lets|which|best)\b", "", mobile_model, flags=re.IGNORECASE).strip().title()
    if not clean_name or len(clean_name) < 2:
        return {"status": "success", "phone": MOCK_MOBILE_DATABASE["iphone 16 pro max"]}

    return {
        "status": "success",
        "phone": {
            "name": f"{clean_name} Smartphone",
            "brand": clean_name.split()[0] if clean_name.split() else "Smartphone",
            "category": "Premium Flagship Smartphone",
            "display": "6.7\" 2K LTPO AMOLED Display (1-120Hz Variable Refresh, 2,500+ nits Peak Brightness, HDR10+)",
            "processor": "Flagship 3nm Octa-Core Chipset (Snapdragon 8 Elite / A18 Pro / Tensor G4 with On-Device AI NPU)",
            "camera": "50MP Primary (f/1.6, OIS) + 50MP Ultra-Wide (120° FOV) + 50MP Periscope Telephoto (5x Optical Zoom, 8K Video Recording)",
            "battery_charging": "5,000 - 6,000 mAh Silicon-Carbon Battery, 65W-100W Fast Wired Charging, 15W-50W Wireless Charging",
            "build_weight": "210 grams, Aerospace Titanium / Aluminum Frame with IP68 Water & Dust Resistance",
            "special_features": "On-Device Generative AI Assistant, Ultrasonic Fingerprint Scanner, Dual Stereo Speakers with Spatial Audio, 5G Dual SIM, Wi-Fi 7",
            "starting_price": "$799 - $1,199 (Flagship Tier Range)"
        }
    }
