import os
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OpenWeather")

@mcp.tool()
async def get_7_day_forecast(location: str) -> str:
    """
    Fetches a 7-day weather forecast for the specified location.
    Provides temperature max/min, precipitation, wind, and alerts for extreme conditions
    (frost, heavy rain, extreme heat) to help identify the best time to plant or harvest.
    """
    try:
        # Check if user has an OpenWeather API key configured
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        
        # We will use Open-Meteo for geocoding and forecasting by default as it is free,
        # requires no API key, and provides real 7-day daily forecasts.
        # If OpenWeather key is set, we can use OpenWeather geocoding and standard APIs,
        # but Open-Meteo is highly reliable for free 7-day forecast.
        
        async with httpx.AsyncClient() as client:
            # 1. Geocode location
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_resp = await client.get(geo_url)
            geo_data = geo_resp.json()
            
            if not geo_data.get("results"):
                # Fallback to realistic mock data if geocoding fails or location is not found
                return get_mock_forecast(location, "Location not found in database. Displaying simulated forecast.")
            
            result = geo_data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            resolved_name = f"{result.get('name')}, {result.get('admin1', '')}, {result.get('country', '')}"
            timezone = result.get("timezone", "auto")
            
            # 2. Get forecast from Open-Meteo daily endpoint
            forecast_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,"
                f"precipitation_sum,precipitation_probability_max,wind_speed_10m_max&timezone={timezone}"
            )
            forecast_resp = await client.get(forecast_url)
            forecast_data = forecast_resp.json()
            
            if "daily" not in forecast_data:
                return get_mock_forecast(resolved_name, "Weather service unavailable. Displaying simulated forecast.")
            
            daily = forecast_data["daily"]
            time_list = daily["time"]
            temp_max = daily["temperature_2m_max"]
            temp_min = daily["temperature_2m_min"]
            precip = daily["precipitation_sum"]
            precip_prob = daily.get("precipitation_probability_max", [0]*len(time_list))
            wind = daily["wind_speed_10m_max"]
            
            # Construct a beautiful forecast report
            report = [
                f"### 7-Day Weather Forecast for {resolved_name}",
                f"Coordinates: Lat {lat:.4f}, Lon {lon:.4f}\n",
                "| Date | Max Temp (°C) | Min Temp (°C) | Rain (mm) | Rain Prob (%) | Max Wind (km/h) |",
                "| --- | --- | --- | --- | --- | --- |"
            ]
            
            has_frost_warning = False
            has_heat_warning = False
            has_heavy_rain_warning = False
            
            best_planting_days = []
            best_harvesting_days = []
            
            for i in range(len(time_list)):
                date = time_list[i]
                t_max = temp_max[i]
                t_min = temp_min[i]
                rain = precip[i]
                r_prob = precip_prob[i]
                w = wind[i]
                
                report.append(f"| {date} | {t_max:.1f}°C | {t_min:.1f}°C | {rain:.1f} mm | {r_prob}% | {w:.1f} km/h |")
                
                # Check for warnings
                if t_min <= 2:
                    has_frost_warning = True
                if t_max >= 38:
                    has_heat_warning = True
                if rain >= 20:
                    has_heavy_rain_warning = True
                
                # Logic for planting/harvesting windows
                # Planting needs moderate temperature, some moisture (rain 2-10mm or moderate probability), low wind
                if 15 <= t_max <= 30 and t_min > 5 and 0 < rain <= 10 and w < 20:
                    best_planting_days.append(date)
                # Harvesting needs dry weather (no rain, low prob) and moderate wind
                if rain == 0 and r_prob < 15 and w < 25:
                    best_harvesting_days.append(date)

            # Compile warnings
            warnings = []
            if has_frost_warning:
                warnings.append("⚠️ **FROST WARNING**: Temperatures are predicted to drop near or below freezing. Cover sensitive young crops.")
            if has_heat_warning:
                warnings.append("⚠️ **HEAT WARNING**: Temperatures are predicted to exceed 38°C. Ensure adequate irrigation to prevent heat stress.")
            if has_heavy_rain_warning:
                warnings.append("⚠️ **HEAVY RAIN WARNING**: High precipitation predicted. Watch for flooding, soil erosion, and fungal diseases.")
            
            report.append("\n**Alerts & Warnings:**")
            if warnings:
                report.extend(warnings)
            else:
                report.append("✅ No immediate weather alerts (frost/extreme heat/heavy storms) for the next 7 days.")
                
            report.append("\n**Farming Advisory:**")
            if best_planting_days:
                report.append(f"- 🌱 **Best Planting Days**: {', '.join(best_planting_days[:3])} (favorable temperature, soil moisture, and low wind).")
            else:
                report.append("- 🌱 **Best Planting Days**: No optimal planting windows in the next 7 days. Soil may be too dry, too wet, or temperatures are unfavorable.")
                
            if best_harvesting_days:
                report.append(f"- 🚜 **Best Harvesting Days**: {', '.join(best_harvesting_days[:3])} (dry, sunny conditions perfect for crop harvesting and drying).")
            else:
                report.append("- 🚜 **Best Harvesting Days**: No dry harvesting windows in the next 7 days. Precipitation may delay field operations.")

            return "\n".join(report)
            
    except Exception as e:
        return get_mock_forecast(location, f"Error calling weather API: {str(e)}. Displaying simulated forecast.")

def get_mock_forecast(location: str, note: str) -> str:
    """Returns realistic mock weather forecast."""
    return f"""### 7-Day Weather Forecast for {location} (Simulated)
*Note: {note}*

| Date | Max Temp (°C) | Min Temp (°C) | Rain (mm) | Rain Prob (%) | Max Wind (km/h) |
| --- | --- | --- | --- | --- | --- |
| Day 1 | 24.5°C | 14.0°C | 0.0 mm | 10% | 12.0 km/h |
| Day 2 | 22.0°C | 13.5°C | 4.2 mm | 60% | 15.0 km/h |
| Day 3 | 19.8°C | 11.0°C | 12.5 mm | 85% | 22.0 km/h |
| Day 4 | 21.0°C | 12.0°C | 1.0 mm | 30% | 14.0 km/h |
| Day 5 | 23.5°C | 13.0°C | 0.0 mm | 5% | 10.0 km/h |
| Day 6 | 25.0°C | 14.5°C | 0.0 mm | 5% | 8.5 km/h |
| Day 7 | 26.2°C | 15.0°C | 0.0 mm | 0% | 11.0 km/h |

**Alerts & Warnings:**
✅ No immediate weather alerts (frost/extreme heat/heavy storms) for the next 7 days.

**Farming Advisory:**
- 🌱 **Best Planting Days**: Day 2, Day 4 (moderate temperature and favorable soil moisture).
- 🚜 **Best Harvesting Days**: Day 5, Day 6, Day 7 (dry, sunny conditions).
"""

if __name__ == "__main__":
    mcp.run()
