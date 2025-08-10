"""
Location and radius management for Potluck
Handles zip codes, distance calculations, and local community boundaries
"""

import math
from typing import Dict, List, Tuple, Optional
import json

class LocationService:
    """Handle location-based operations"""
    
    # Default service radius in km
    DEFAULT_RADIUS_KM = 3.0  # 3km radius for bicycle delivery
    
    # Sample zip code coordinates (in production, use a proper geocoding API)
    # Format: zip_code: (latitude, longitude, city, state)
    ZIP_COORDINATES = {
        # Dallas, TX area
        '75201': (32.7815, -96.7968, 'Dallas', 'TX'),
        '75202': (32.7831, -96.8067, 'Dallas', 'TX'),
        '75203': (32.7459, -96.7838, 'Dallas', 'TX'),
        '75204': (32.8007, -96.7699, 'Dallas', 'TX'),
        '75205': (32.8137, -96.7943, 'Dallas', 'TX'),
        '75206': (32.7700, -96.7643, 'Dallas', 'TX'),
        
        # Add more zip codes as needed
        # Mumbai, India examples
        '400001': (18.9388, 72.8354, 'Mumbai', 'MH'),
        '400002': (18.9497, 72.8323, 'Mumbai', 'MH'),
        
        # Mexico City examples  
        '01000': (19.3500, -99.1600, 'Mexico City', 'CDMX'),
        '01010': (19.3550, -99.1650, 'Mexico City', 'CDMX'),
    }
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, 
                         lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def get_coordinates_from_zip(zip_code: str) -> Optional[Tuple[float, float, str, str]]:
        """
        Get coordinates from zip/postal code
        Returns: (latitude, longitude, city, state) or None
        """
        # Remove spaces and convert to uppercase for consistency
        zip_clean = zip_code.replace(' ', '').upper()
        
        # Check our database first
        if zip_clean in LocationService.ZIP_COORDINATES:
            return LocationService.ZIP_COORDINATES[zip_clean]
        
        # For 5-digit US zip codes, try without leading zeros
        if len(zip_clean) == 5 and zip_clean.isdigit():
            if zip_clean in LocationService.ZIP_COORDINATES:
                return LocationService.ZIP_COORDINATES[zip_clean]
        
        # In production, call a geocoding API here
        # For now, return None if not found
        return None
    
    @staticmethod
    def validate_service_area(chef_zip: str, customer_zip: str, 
                            max_radius_km: float = None) -> Dict:
        """
        Check if customer is within chef's service area
        """
        if max_radius_km is None:
            max_radius_km = LocationService.DEFAULT_RADIUS_KM
        
        chef_coords = LocationService.get_coordinates_from_zip(chef_zip)
        customer_coords = LocationService.get_coordinates_from_zip(customer_zip)
        
        if not chef_coords or not customer_coords:
            return {
                'serviceable': False,
                'reason': 'Invalid zip code',
                'distance': None
            }
        
        distance = LocationService.calculate_distance(
            chef_coords[0], chef_coords[1],
            customer_coords[0], customer_coords[1]
        )
        
        return {
            'serviceable': distance <= max_radius_km,
            'distance': round(distance, 2),
            'max_radius': max_radius_km,
            'chef_location': f"{chef_coords[2]}, {chef_coords[3]}",
            'customer_location': f"{customer_coords[2]}, {customer_coords[3]}"
        }
    
    @staticmethod
    def find_nearby_chefs(customer_zip: str, radius_km: float = None) -> List[Dict]:
        """
        Find all chefs within radius of customer
        """
        if radius_km is None:
            radius_km = LocationService.DEFAULT_RADIUS_KM
        
        customer_coords = LocationService.get_coordinates_from_zip(customer_zip)
        if not customer_coords:
            return []
        
        nearby_chefs = []
        
        # In production, query database for chef locations
        # For demo, check against sample data
        sample_chef_zips = ['75201', '75202', '75203']  # Example chef locations
        
        for chef_zip in sample_chef_zips:
            chef_coords = LocationService.get_coordinates_from_zip(chef_zip)
            if chef_coords:
                distance = LocationService.calculate_distance(
                    customer_coords[0], customer_coords[1],
                    chef_coords[0], chef_coords[1]
                )
                
                if distance <= radius_km:
                    nearby_chefs.append({
                        'zip': chef_zip,
                        'distance': round(distance, 2),
                        'location': f"{chef_coords[2]}, {chef_coords[3]}"
                    })
        
        # Sort by distance
        nearby_chefs.sort(key=lambda x: x['distance'])
        return nearby_chefs
    
    @staticmethod
    def find_delivery_agents_in_range(order_pickup_zip: str, 
                                     order_delivery_zip: str,
                                     max_radius_km: float = None) -> List[Dict]:
        """
        Find delivery agents who can handle the order
        Agent must be within radius of BOTH pickup and delivery
        """
        if max_radius_km is None:
            max_radius_km = LocationService.DEFAULT_RADIUS_KM
        
        pickup_coords = LocationService.get_coordinates_from_zip(order_pickup_zip)
        delivery_coords = LocationService.get_coordinates_from_zip(order_delivery_zip)
        
        if not pickup_coords or not delivery_coords:
            return []
        
        # Calculate total trip distance
        trip_distance = LocationService.calculate_distance(
            pickup_coords[0], pickup_coords[1],
            delivery_coords[0], delivery_coords[1]
        )
        
        # Don't allow deliveries beyond service radius
        if trip_distance > max_radius_km:
            return []
        
        eligible_agents = []
        
        # In production, query database for online delivery agents
        # For demo, use sample data
        sample_agent_zips = ['75201', '75204', '75205']
        
        for agent_zip in sample_agent_zips:
            agent_coords = LocationService.get_coordinates_from_zip(agent_zip)
            if agent_coords:
                # Check distance to pickup
                pickup_distance = LocationService.calculate_distance(
                    agent_coords[0], agent_coords[1],
                    pickup_coords[0], pickup_coords[1]
                )
                
                # Agent should be within reasonable distance of pickup
                if pickup_distance <= max_radius_km:
                    eligible_agents.append({
                        'zip': agent_zip,
                        'distance_to_pickup': round(pickup_distance, 2),
                        'total_trip': round(trip_distance, 2),
                        'location': f"{agent_coords[2]}, {agent_coords[3]}"
                    })
        
        # Sort by distance to pickup
        eligible_agents.sort(key=lambda x: x['distance_to_pickup'])
        return eligible_agents
    
    @staticmethod
    def get_local_market_info(zip_code: str) -> Dict:
        """
        Get local market information for pricing
        """
        coords = LocationService.get_coordinates_from_zip(zip_code)
        
        if not coords:
            return {
                'location': 'Unknown',
                'pricing_tier': 'medium',
                'currency': 'USD',
                'currency_symbol': '$'
            }
        
        city = coords[2]
        state = coords[3]
        
        # Define pricing tiers and currency by location
        market_data = {
            # USA Cities
            'Dallas': {'tier': 'medium', 'currency': 'USD', 'symbol': '$'},
            'San Francisco': {'tier': 'high', 'currency': 'USD', 'symbol': '$'},
            'New York': {'tier': 'high', 'currency': 'USD', 'symbol': '$'},
            
            # India Cities
            'Mumbai': {'tier': 'medium', 'currency': 'INR', 'symbol': '₹'},
            'Delhi': {'tier': 'medium', 'currency': 'INR', 'symbol': '₹'},
            'Bangalore': {'tier': 'medium', 'currency': 'INR', 'symbol': '₹'},
            
            # Mexico Cities
            'Mexico City': {'tier': 'low', 'currency': 'MXN', 'symbol': '$'},
            'Guadalajara': {'tier': 'low', 'currency': 'MXN', 'symbol': '$'},
        }
        
        # Get market info for the city
        city_data = market_data.get(city, {'tier': 'medium', 'currency': 'USD', 'symbol': '$'})
        
        return {
            'location': f"{city}, {state}",
            'city': city,
            'state': state,
            'pricing_tier': city_data['tier'],
            'currency': city_data['currency'],
            'currency_symbol': city_data['symbol'],
            'coordinates': {
                'latitude': coords[0],
                'longitude': coords[1]
            }
        }
    @staticmethod
    def format_address_with_zip(address: str, zip_code: str) -> str:
        """
        Format full address with zip code
        """
        coords = LocationService.get_coordinates_from_zip(zip_code)
        if coords:
            return f"{address}, {coords[2]}, {coords[3]} {zip_code}"
        return f"{address} {zip_code}"


# Singleton instance
location_service = LocationService()