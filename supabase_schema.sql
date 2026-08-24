-- ============================================================================
-- Supabase SQL Schema for Gemini Chatbot Chat History
-- Copy and run this script in the Supabase SQL Editor (https://supabase.com/dashboard)
-- ============================================================================

-- 1. Table: chat_sessions
-- Stores conversation metadata (session ID, title/preview, timestamp, total messages)
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    title TEXT DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    message_count INTEGER DEFAULT 0
);

-- 2. Table: chat_messages
-- Stores individual message turns (role, content, tools used, timestamps)
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES public.chat_sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tools JSONB DEFAULT '[]'::jsonb,
    timestamp TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON public.chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON public.chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at ASC);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- 5. Open Policies for Anonymous / Authenticated Client Access
-- Allows the chatbot UI using the public 'anon' key to read, insert, update, and delete chat history
DROP POLICY IF EXISTS "Allow all operations on chat_sessions" ON public.chat_sessions;
CREATE POLICY "Allow all operations on chat_sessions"
    ON public.chat_sessions
    FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations on chat_messages" ON public.chat_messages;
CREATE POLICY "Allow all operations on chat_messages"
    ON public.chat_messages
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- 6. Table: holiday_packages
-- Stores curated holiday destinations, tiered hotels, and transport fares
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.holiday_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_key TEXT UNIQUE NOT NULL,
    destination_name TEXT NOT NULL,
    tagline TEXT,
    category TEXT,
    best_time_to_visit TEXT,
    key_attractions TEXT[],
    hotels JSONB NOT NULL,
    transport_fares JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.holiday_packages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations on holiday_packages" ON public.holiday_packages;
CREATE POLICY "Allow all operations on holiday_packages"
    ON public.holiday_packages
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Insert Seed Data for the 5 Destinations (Ujjain, Kashmir, Manali, Goa, Rajasthan)
INSERT INTO public.holiday_packages (destination_key, destination_name, tagline, category, best_time_to_visit, key_attractions, hotels, transport_fares)
VALUES
(
    'ujjain',
    'Ujjain',
    'The Holy City of Mahakal — Jyotirlinga Darshan, Bhasma Aarti & Sacred Ghats',
    'Spiritual & Pilgrimage Destination',
    'October to March',
    ARRAY['Mahakaleshwar Jyotirlinga (Live Bhasma Aarti)', 'Mahakal Lok Corridor', 'Ram Ghat (Shipra River Aarti)', 'Kal Bhairav Temple', 'Harsiddhi Mata Shaktipeeth'],
    '{
        "cheapest": {"tier": "Budget / Ashram Yatri Niwas", "name": "Mahakal Bhakt Niwas / Clean Ghat Ashrams", "price_per_night": 600, "rating": "4.2 ★"},
        "comfort": {"tier": "3-Star Comfort", "name": "Hotel Imperial Ujjain / Anjushree Courtyard", "price_per_night": 2200, "rating": "4.4 ★"},
        "premium": {"tier": "4-Star Luxury", "name": "Hotel Abika Elite / Anjushree Luxury Resort", "price_per_night": 5500, "rating": "4.6 ★"},
        "richest": {"tier": "5-Star Heritage Sanctuary", "name": "Rudraksh Club & Resort / Shipra Heritage Suite", "price_per_night": 14000, "rating": "4.8 ★"}
    }'::jsonb,
    '{
        "mumbai": {"train_sleeper": 650, "train_3ac": 1650, "train_2ac": 2350, "flight_return": 4800},
        "delhi": {"train_sleeper": 700, "train_3ac": 1750, "train_2ac": 2500, "flight_return": 5200},
        "ahmedabad": {"train_sleeper": 400, "train_3ac": 1050, "train_2ac": 1500, "flight_return": 4200},
        "pune": {"train_sleeper": 650, "train_3ac": 1600, "train_2ac": 2300, "flight_return": 5400},
        "bengaluru": {"train_sleeper": 1500, "train_3ac": 3800, "train_2ac": 5400, "flight_return": 6500}
    }'::jsonb
),
(
    'kashmir',
    'Kashmir',
    'Paradise on Earth — Dal Lake Houseboats, Snow Gondola & Chinar Valleys',
    'Scenic Valleys, Snow & Alpine Paradise',
    'March to October (Summer) / Dec to Feb (Snow & Skiing)',
    ARRAY['Dal Lake Shikara & Houseboat', 'Gulmarg Gondola & Skiing', 'Pahalgam Betaab Valley', 'Sonamarg Thajiwas Glacier', 'Mughal Gardens'],
    '{
        "cheapest": {"tier": "Budget Homestay", "name": "Zostel Srinagar / Kashmiri Family Homestay", "price_per_night": 1200, "rating": "4.3 ★"},
        "comfort": {"tier": "3-Star Deluxe Hotel", "name": "Hotel Grand Mumtaz / Pine Palace Gulmarg", "price_per_night": 3800, "rating": "4.5 ★"},
        "premium": {"tier": "4-Star Luxury Houseboat", "name": "Heritage Walnut Houseboat on Nigeen Lake", "price_per_night": 11000, "rating": "4.7 ★"},
        "richest": {"tier": "5-Star Himalayan Sanctuary", "name": "The Khyber Himalayan Resort & Spa Gulmarg", "price_per_night": 34000, "rating": "4.9 ★"}
    }'::jsonb,
    '{
        "delhi": {"train_sleeper": 1200, "train_3ac": 2800, "train_2ac": 4100, "flight_return": 6500},
        "mumbai": {"train_sleeper": 1800, "train_3ac": 4400, "train_2ac": 6400, "flight_return": 9800},
        "bengaluru": {"train_sleeper": null, "train_3ac": null, "train_2ac": null, "flight_return": 11500},
        "pune": {"train_sleeper": null, "train_3ac": null, "train_2ac": null, "flight_return": 10500},
        "ahmedabad": {"train_sleeper": 1400, "train_3ac": 3600, "train_2ac": 5200, "flight_return": 9200}
    }'::jsonb
),
(
    'manali',
    'Manali',
    'Snow-Capped Peaks, Pine Forests & Adventure Sports',
    'Hill Station & Adventure Hub',
    'October to June (Dec-Feb for Snow)',
    ARRAY['Solang Valley', 'Atal Tunnel & Sissu', 'Rohtang Pass', 'Hadimba Temple', 'Jogini Waterfall'],
    '{
        "cheapest": {"tier": "Budget Hostel", "name": "The Hosteller / Zostel Old Manali", "price_per_night": 950, "rating": "4.3 ★"},
        "comfort": {"tier": "3-Star Comfort", "name": "Snow Valley Resorts", "price_per_night": 3200, "rating": "4.4 ★"},
        "premium": {"tier": "4-Star Mountain Resort", "name": "The Himalayan Castle Resort & Spa", "price_per_night": 9200, "rating": "4.7 ★"},
        "richest": {"tier": "5-Star Ultra-Luxury", "name": "Span Resort & Spa / Larisa Resort", "price_per_night": 24000, "rating": "4.9 ★"}
    }'::jsonb,
    '{
        "delhi": {"train_sleeper": 1200, "train_3ac": 2600, "train_2ac": 3800, "flight_return": 9500},
        "mumbai": {"train_sleeper": 2400, "train_3ac": 5400, "train_2ac": 7800, "flight_return": 11500},
        "bengaluru": {"train_sleeper": null, "train_3ac": null, "train_2ac": null, "flight_return": 12500},
        "pune": {"train_sleeper": null, "train_3ac": null, "train_2ac": null, "flight_return": 11800}
    }'::jsonb
),
(
    'goa',
    'Goa',
    'Sun, Sand, Beaches & Vibrant Nightlife',
    'Beach & Leisure Destination',
    'October to March',
    ARRAY['Baga Beach', 'Dudhsagar Falls', 'Aguada Fort', 'Anjuna Flea Market', 'Basilica of Bom Jesus'],
    '{
        "cheapest": {"tier": "Budget Hostel", "name": "Zostel / Goa Beach Backpackers", "price_per_night": 1200, "rating": "4.2 ★"},
        "comfort": {"tier": "3-Star Comfort", "name": "Lemon Tree Hotel / BloomSuites", "price_per_night": 3800, "rating": "4.5 ★"},
        "premium": {"tier": "4-Star Resort", "name": "Novotel Resort & Spa / Radisson Blu", "price_per_night": 8500, "rating": "4.6 ★"},
        "richest": {"tier": "5-Star Ultra-Luxury", "name": "The Leela Goa / Taj Exotica", "price_per_night": 28000, "rating": "4.9 ★"}
    }'::jsonb,
    '{
        "mumbai": {"train_sleeper": 900, "train_3ac": 2400, "train_2ac": 3600, "flight_return": 5500},
        "delhi": {"train_sleeper": 1600, "train_3ac": 4200, "train_2ac": 6200, "flight_return": 8800},
        "bengaluru": {"train_sleeper": 850, "train_3ac": 2200, "train_2ac": 3300, "flight_return": 4800},
        "pune": {"train_sleeper": 800, "train_3ac": 2100, "train_2ac": 3100, "flight_return": 5200},
        "hyderabad": {"train_sleeper": 1100, "train_3ac": 2800, "train_2ac": 4000, "flight_return": 6200}
    }'::jsonb
),
(
    'rajasthan',
    'Rajasthan (Jaipur & Udaipur)',
    'Majestic Forts, Royal Palaces & Rich Rajasthani Culture',
    'Heritage & Royal Tourism',
    'October to March',
    ARRAY['Amer Fort', 'Hawa Mahal', 'City Palace', 'Nahargarh Fort', 'Chokhi Dhani', 'Lake Pichola Udaipur'],
    '{
        "cheapest": {"tier": "Budget Haveli Hostel", "name": "Moustache Jaipur / Zostel Haveli", "price_per_night": 850, "rating": "4.3 ★"},
        "comfort": {"tier": "3-Star Heritage Hotel", "name": "Alsisar Haveli / Mandawa Haveli", "price_per_night": 3500, "rating": "4.5 ★"},
        "premium": {"tier": "4-Star Royal Palace", "name": "Samode Haveli / ITC Rajputana", "price_per_night": 10500, "rating": "4.7 ★"},
        "richest": {"tier": "5-Star World-Class Palace", "name": "Rambagh Palace / Taj Lake Palace", "price_per_night": 42000, "rating": "5.0 ★"}
    }'::jsonb,
    '{
        "delhi": {"train_sleeper": 500, "train_3ac": 1400, "train_2ac": 2100, "flight_return": 4200},
        "mumbai": {"train_sleeper": 1100, "train_3ac": 2800, "train_2ac": 4100, "flight_return": 6500},
        "bengaluru": {"train_sleeper": 1800, "train_3ac": 4600, "train_2ac": 6800, "flight_return": 8200},
        "ahmedabad": {"train_sleeper": 600, "train_3ac": 1600, "train_2ac": 2400, "flight_return": 4800}
    }'::jsonb
)
ON CONFLICT (destination_key) DO UPDATE
SET
    hotels = EXCLUDED.hotels,
    transport_fares = EXCLUDED.transport_fares,
    key_attractions = EXCLUDED.key_attractions;


