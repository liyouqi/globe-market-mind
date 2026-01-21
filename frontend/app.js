document.addEventListener('DOMContentLoaded', () => {
    // Initialize map with bounds to prevent infinite scrolling into empty space
    const bounds = L.latLngBounds(L.latLng(-90, -180), L.latLng(90, 180));
    const map = L.map('map', {
        maxBounds: bounds,
        maxBoundsViscosity: 1.0,
        minZoom: 2
    }).setView([20, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        noWrap: true,
        bounds: bounds
    }).addTo(map);

    let geoJsonLayer;
    let marketData = [];
    let stateData = [];

    // Color interpolation: -1 (Red) -> 0 (Yellow) -> 1 (Green)
    function getColor(mood) {
        if (mood === null || mood === undefined) return '#808080'; // Grey for no data

        let r, g, b;
        if (mood < 0) {
            // -1 to 0: Red to Yellow
            const ratio = Math.max(0, mood + 1); // 0 to 1
            r = 255;
            g = Math.floor(255 * ratio);
            b = 0;
        } else {
            // 0 to 1: Yellow to Green
            const ratio = Math.min(1, mood); // 0 to 1
            r = Math.floor(255 * (1 - ratio));
            g = 255;
            b = 0;
        }
        return `rgb(${r}, ${g}, ${b})`;
    }

    function style(feature) {
        const countryName = feature.properties.name;
        const mood = getCountryMood(countryName);
        return {
            fillColor: getColor(mood),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }

    // Helper to get mean mood for a country name
    function getCountryMood(countryName) {
        // 1. Find markets for this country
        const countryMarkets = marketData.filter(m => {
            if (!m.country) return false;
            const marketCountry = m.country.toLowerCase();
            const geoCountry = countryName.toLowerCase();

            // Alias handling for specific backend codes
            if (m.country === "USA" && (geoCountry === "united states" || geoCountry === "united states of america")) return true;
            if (m.country === "UK" && (geoCountry === "united kingdom" || geoCountry === "great britain")) return true;
            if (m.country === "UAE" && (geoCountry === "united arab emirates")) return true;

            // Default loose matching
            return (marketCountry === geoCountry || 
                    geoCountry.includes(marketCountry) || 
                    marketCountry.includes(geoCountry));
        });

        if (countryMarkets.length === 0) return null;

        // 2. Find states for these markets
        let totalMood = 0;
        let count = 0;

        countryMarkets.forEach(market => {
            // Find latest state for this market
            const marketStates = stateData.filter(s => s.market_id === market.id);
            if (marketStates.length > 0) {
                 // Sort by date desc
                 marketStates.sort((a, b) => new Date(b.date) - new Date(a.date));
                 const latestState = marketStates[0];
                 
                 // Use mood_index
                 if (latestState.mood_index !== undefined && latestState.mood_index !== null) {
                     totalMood += latestState.mood_index;
                     count++;
                 }
            }
        });

        return count > 0 ? totalMood / count : null;
    }
    
    function onEachFeature(feature, layer) {
        const countryName = feature.properties.name;
        const mood = getCountryMood(countryName);
        
        let moodText = "No Data";
        if (mood !== null) {
            moodText = mood.toFixed(4);
        }
        
        layer.bindPopup(`<strong>${countryName}</strong><br>Mood Index: ${moodText}`);
        
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
        });
    }

    function highlightFeature(e) {
        var layer = e.target;
        layer.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
        });
        layer.bringToFront();
    }

    function resetHighlight(e) {
        geoJsonLayer.resetStyle(e.target);
    }

    async function loadData() {
        try {
            const [marketsRes, statesRes] = await Promise.all([
                fetch('/api/data/markets'),
                fetch('/api/data/daily_state')
            ]);
            
            if (!marketsRes.ok || !statesRes.ok) throw new Error("Failed to fetch API data");

            marketData = await marketsRes.json();
            stateData = await statesRes.json();
            
            // Determine "Last Updated" based on latest state date
            if (stateData.length > 0) {
                 const dates = stateData.map(s => new Date(s.date));
                 const maxDate = new Date(Math.max.apply(null, dates));
                 document.getElementById('last-updated').textContent = "Last Data: " + maxDate.toLocaleDateString();
            } else {
                 document.getElementById('last-updated').textContent = "Last Data: None";
            }

            updateMap();
        } catch (error) {
            console.error(error);
            alert("Error loading data. Make sure backend is running and analysis has been triggered.");
        }
    }

    async function updateMap() {
        // Fetch GeoJSON if not loaded
        if (!geoJsonLayer) {
            try {
                // Using a reliable source for world countries GeoJSON
                const response = await fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json');
                const data = await response.json();
                
                geoJsonLayer = L.geoJson(data, {
                    style: style,
                    onEachFeature: onEachFeature
                }).addTo(map);
            } catch (e) {
                console.error("Failed to load GeoJSON", e);
            }
        } else {
            geoJsonLayer.setStyle(style);
        }
    }
    
    // Initial Load
    loadData();

    // Event Listeners
    document.getElementById('refresh-btn').addEventListener('click', loadData);
    
    document.getElementById('analyze-btn').addEventListener('click', async () => {
        const btn = document.getElementById('analyze-btn');
        btn.disabled = true;
        btn.textContent = "Analyzing...";
        
        try {
            const res = await fetch('/api/process/analyze', { method: 'POST' });
            if (res.ok) {
                alert("Analysis complete! Refreshing map...");
                loadData();
            } else {
                const err = await res.json();
                alert("Analysis failed: " + (err.error || "Unknown error"));
            }
        } catch (e) {
            console.error(e);
            alert("Error triggering analysis");
        } finally {
            btn.disabled = false;
            btn.textContent = "Trigger Analysis (Daily)";
        }
    });
});
