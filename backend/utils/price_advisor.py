"""
AI-powered Price Advisor for Potluck
Uses Anthropic Claude to suggest competitive pricing based on actual costs
"""

import os
import json
from typing import Dict, Tuple
import anthropic
from dotenv import load_dotenv

load_dotenv()

class PriceAdvisor:
    """AI-powered pricing suggestions for home chefs"""
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.has_api_key = bool(api_key and api_key != '')
        
        if self.has_api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                print("✅ AI Price Advisor initialized with Anthropic API")
            except Exception as e:
                print(f"⚠️ Failed to initialize Anthropic client: {e}")
                self.has_api_key = False
                self.client = None
        else:
            print("ℹ️ AI Price Advisor running in fallback mode (no API key)")
            self.client = None
    
    def get_price_suggestion(self, dish_data: Dict) -> Dict:
        """
        Get AI-powered price suggestion for a dish
        
        Args:
            dish_data: {
                'name': 'Dish name',
                'cuisine': 'Cuisine type',
                'ingredients': ['ingredient1', 'ingredient2'],
                'portion_size': 'Serves 2',
                'location': 'City, State',  # From user's zip code
                'chef_rating': 4.5,  # Optional
                'chef_experience': 'new'  # new, intermediate, experienced
            }
        """
        
        # Build context for AI
        prompt = f"""You are a pricing expert for a homemade food marketplace app.
        
        A home chef wants to price this dish:
        - Dish: {dish_data.get('name')}
        - Cuisine: {dish_data.get('cuisine')}
        - Ingredients: {', '.join(dish_data.get('ingredients', []))}
        - Portion: {dish_data.get('portion_size')}
        - Location: {dish_data.get('location', 'your area')}
        - Currency: {dish_data.get('currency', 'USD')} ({dish_data.get('currency_symbol', '$')})
        - Chef Experience: {dish_data.get('chef_experience', 'new')}
        
        Calculate price based on ACTUAL COSTS:
        1. Ingredient costs in {dish_data.get('location', 'local market')} in {dish_data.get('currency', 'local currency')}
        2. Home cooking costs:
           - Gas/electricity for cooking (minimal, using home utilities)
           - Chef's time (30-60 mins preparation)
           - Packaging costs
           - Platform fee (10% of price)
        3. Profit margin:
           - New chefs: 20-30% profit margin
           - Intermediate chefs: 30-40% profit margin  
           - Experienced chefs: 40-50% profit margin
        
        DO NOT base price on restaurant prices. Calculate from actual costs.
        Example: If ingredients cost $5, utilities $0.50, packaging $0.50, 
        the base cost is $6. With 30% margin = $7.80, plus platform fee = $8.60
        
        Also provide restaurant price for reference (NOT for calculation).
        
        Provide a JSON response with:
        {{
            "suggested_price": <calculated from costs + margin>,
            "min_price": <minimum viable price with 20% margin>,
            "max_price": <maximum with 50% margin>,
            "restaurant_comparison": <typical restaurant price for reference>,
            "cost_breakdown": {{
                "ingredients": <cost>,
                "utilities": <cost>,
                "packaging": <cost>,
                "platform_fee": <cost>,
                "profit": <amount>
            }},
            "reasoning": "<explain the calculation>",
            "tips": "<pricing strategy tips>"
        }}
        
        Only respond with valid JSON, no other text."""
        
        # Use fallback if no API key
        if not self.has_api_key or not self.client:
            return self._fallback_pricing(dish_data)
        
        try:
            # Call Anthropic API
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Using Haiku for cost efficiency
                max_tokens=600,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            pricing_data = json.loads(response_text)
            
            # Validate that price is reasonable for new chefs
            if dish_data.get('chef_experience', 'new') == 'new':
                # Ensure new chefs have competitive pricing
                if 'cost_breakdown' in pricing_data:
                    total_cost = sum([
                        pricing_data['cost_breakdown'].get('ingredients', 0),
                        pricing_data['cost_breakdown'].get('utilities', 0),
                        pricing_data['cost_breakdown'].get('packaging', 0)
                    ])
                    
                    # New chefs should have 20-30% margin max
                    max_price = total_cost * 1.3 * 1.1  # 30% margin + 10% platform
                    
                    if pricing_data['suggested_price'] > max_price:
                        pricing_data['suggested_price'] = round(max_price, 2)
            
            return {
                'success': True,
                'pricing': pricing_data
            }
            
        except json.JSONDecodeError:
            # Fallback to rule-based pricing if AI fails
            return self._fallback_pricing(dish_data)
        except Exception as e:
            print(f"Error getting AI price suggestion: {e}")
            return self._fallback_pricing(dish_data)
    
    def _fallback_pricing(self, dish_data: Dict) -> Dict:
        """Fallback rule-based pricing when AI is unavailable"""
        
        # Cost-based pricing for different cuisines (estimated ingredient costs)
        base_costs = {
            'Indian': {'ingredients': 5, 'utilities': 0.5, 'packaging': 0.5},
            'Mexican': {'ingredients': 4, 'utilities': 0.4, 'packaging': 0.5},
            'Italian': {'ingredients': 6, 'utilities': 0.6, 'packaging': 0.5},
            'Chinese': {'ingredients': 4.5, 'utilities': 0.5, 'packaging': 0.5},
            'American': {'ingredients': 5.5, 'utilities': 0.4, 'packaging': 0.5},
            'Thai': {'ingredients': 4.5, 'utilities': 0.5, 'packaging': 0.5},
            'Mediterranean': {'ingredients': 5.5, 'utilities': 0.5, 'packaging': 0.5}
        }
        
        costs = base_costs.get(dish_data.get('cuisine'), 
                               {'ingredients': 5, 'utilities': 0.5, 'packaging': 0.5})
        
        # Adjust for portion size
        portion = dish_data.get('portion_size', '').lower()
        multiplier = 1.0
        if 'family' in portion or 'serves 4' in portion:
            multiplier = 2.5
        elif 'serves 3' in portion:
            multiplier = 1.8
        elif 'serves 2' in portion:
            multiplier = 1.3
        
        # Calculate actual costs
        ingredient_cost = costs['ingredients'] * multiplier
        utility_cost = costs['utilities'] * multiplier
        packaging_cost = costs['packaging']
        base_cost = ingredient_cost + utility_cost + packaging_cost
        
        # Profit margins based on experience
        profit_margins = {
            'new': 0.25,        # 25% profit margin
            'intermediate': 0.35,  # 35% profit margin
            'experienced': 0.45    # 45% profit margin
        }
        margin = profit_margins.get(dish_data.get('chef_experience', 'new'), 0.25)
        
        # Calculate price with margin
        price_with_margin = base_cost * (1 + margin)
        # Add platform fee (10%)
        final_price = price_with_margin * 1.1
        
        suggested = round(final_price, 2)
        min_price = round(base_cost * 1.2 * 1.1, 2)  # 20% margin minimum
        max_price = round(base_cost * 1.5 * 1.1, 2)  # 50% margin maximum
        
        return {
            'success': True,
            'pricing': {
                'suggested_price': suggested,
                'min_price': min_price,
                'max_price': max_price,
                'restaurant_comparison': round(suggested * 2.5, 2),  # Restaurants typically 2.5x
                'cost_breakdown': {
                    'ingredients': round(ingredient_cost, 2),
                    'utilities': round(utility_cost, 2),
                    'packaging': round(packaging_cost, 2),
                    'platform_fee': round(final_price - price_with_margin, 2),
                    'profit': round(price_with_margin - base_cost, 2)
                },
                'reasoning': f'Price calculated from actual costs: ingredients ${ingredient_cost:.2f} + utilities ${utility_cost:.2f} + packaging ${packaging_cost:.2f} = ${base_cost:.2f}. Added {int(margin*100)}% profit margin and 10% platform fee.',
                'tips': 'Focus on quality and consistency to build customer trust. Your competitive pricing based on actual costs will attract customers while maintaining profitability.'
            },
            'fallback': True
        }
    
    def validate_price_change(self, chef_id: int, old_price: float, 
                            new_price: float, chef_stats: Dict) -> Dict:
        """
        Validate if a chef can change their price based on credibility
        
        Args:
            chef_id: Chef's ID
            old_price: Current price
            new_price: Proposed new price
            chef_stats: {
                'total_orders': number,
                'rating': number,
                'months_active': number
            }
        """
        
        # Calculate allowed price change based on credibility
        credibility_score = self._calculate_credibility(chef_stats)
        
        # New chefs can only adjust ±10%
        # Experienced chefs can adjust ±30%
        max_change_percent = 10 + (credibility_score * 20)  # 10% to 30%
        
        price_change_percent = abs((new_price - old_price) / old_price * 100)
        
        if price_change_percent <= max_change_percent:
            return {
                'allowed': True,
                'message': 'Price change approved',
                'new_price': new_price
            }
        else:
            suggested_max = old_price * (1 + max_change_percent / 100)
            suggested_min = old_price * (1 - max_change_percent / 100)
            
            return {
                'allowed': False,
                'message': f'Price change too large. Build more credibility first.',
                'max_allowed': round(suggested_max, 2),
                'min_allowed': round(suggested_min, 2),
                'credibility_score': credibility_score,
                'suggestion': 'Complete more orders and maintain high ratings to unlock larger price changes.'
            }
    
    def _calculate_credibility(self, chef_stats: Dict) -> float:
        """
        Calculate chef credibility score (0-1)
        Based on orders, ratings, and time active
        """
        
        orders = chef_stats.get('total_orders', 0)
        rating = chef_stats.get('rating', 0)
        months = chef_stats.get('months_active', 0)
        
        # Scoring weights
        order_score = min(orders / 50, 1.0) * 0.4  # Max at 50 orders
        rating_score = (rating / 5) * 0.4  # Rating out of 5
        time_score = min(months / 6, 1.0) * 0.2  # Max at 6 months
        
        return order_score + rating_score + time_score
    
    def get_market_analysis(self, location: str, cuisine: str) -> Dict:
        """Get market analysis for a location and cuisine type"""
        
        prompt = f"""Analyze the food market in {location} for {cuisine} cuisine.
        
        Focus on:
        1. Average ingredient costs in local markets
        2. Typical portion sizes and pricing
        3. Local demand for this cuisine
        4. Competition from other home chefs
        
        DO NOT base homemade prices on restaurant prices.
        Calculate based on actual costs + reasonable margins.
        
        Provide a brief JSON response with:
        {{
            "average_restaurant_price": <for reference only>,
            "suggested_homemade_price": <based on costs + 30% margin>,
            "ingredient_cost_range": {{"min": <number>, "max": <number>}},
            "popular_dishes": ["dish1", "dish2", "dish3"],
            "demand_level": "low|medium|high",
            "competition_level": "low|medium|high"
        }}
        
        Only respond with valid JSON."""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return json.loads(response_text)
            
        except:
            # Fallback data
            return {
                "average_restaurant_price": 20,
                "suggested_homemade_price": 8,  # Based on costs
                "ingredient_cost_range": {"min": 4, "max": 8},
                "popular_dishes": ["Various dishes"],
                "demand_level": "medium",
                "competition_level": "medium"
            }


# Singleton instance
price_advisor = PriceAdvisor()