---
name: weather_forecast
track: bonus
kind: live_api
provider: Open-Meteo
requires_env: []
inputs: [city, days, unit]
outputs: [location, current, daily]
side_effect: false
---
# weather_forecast

Fetches current weather and daily temperature/precipitation forecast (1-7 days)
for a given city via Open-Meteo.
