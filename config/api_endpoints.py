# U.S. Government Public API Endpoints
API_ENDPOINTS = {
    # NHTSA APIs
    "nhtsa_recalls": "https://api.nhtsa.gov/recalls/recallsByVehicle",
    "nhtsa_fars": "https://crashviewer.nhtsa.dot.gov/CrashAPI",
    "nhtsa_vin": "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/",
    
    # EPA APIs
    "epa_fueleconomy": "https://www.fueleconomy.gov/ws/rest/vehicle/menu/modelYear",
    "epa_emissions": "https://www.epa.gov/web-services",
    
    # FHWA Data
    "fhwa_vmt": "https://www.fhwa.dot.gov/policyinformation/tables/vmt/",
    
    # Census Bureau
    "census_acs": "https://api.census.gov/data/2022/acs/acs5",
    
    # EIA (Energy Information Administration)
    "eia_fuel": "https://api.eia.gov/v2/",
    
    # BEA (Bureau of Economic Analysis)
    "bea_gdp": "https://apps.bea.gov/api/data/"
}

# State FIPS codes (needed for APIs)
STATE_FIPS = {
    'CA': '06', 'TX': '48', 'NY': '36', 'FL': '12',
    'IL': '17', 'PA': '42', 'OH': '39', 'GA': '13'
}