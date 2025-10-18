# 🌍 Service Area Validation Rules

## Business Logic Overview

Potluck uses a **chef-centric expansion model** where chefs create service areas simply by signing up and offering their services.

---

## 📋 User Type Rules

### 👨‍🍳 **CHEFS**
**Can signup: ANYWHERE in the world** ✅

- **No location restrictions**
- Chefs CREATE new service areas by their presence
- First chef in an area pioneers that market
- They define where the platform operates

**Example:**
```
Chef in Dallas, TX → ✅ Approved
Chef in Paris, France → ✅ Approved
Chef in Tokyo, Japan → ✅ Approved
Chef in Random Village → ✅ Approved
```

**Message shown:**
- If new area: *"Welcome Chef! You can start serving in this area. You'll be pioneering food service in this area!"*
- If area has other chefs: *"Welcome Chef! You can start serving in this area."*

---

### 👤 **CONSUMERS**
**Can signup: ANYWHERE** ✅ (but with warnings if no local chefs)

- **No blocking restrictions**
- Can signup even if no chefs in their area
- System finds and shows nearest available chefs
- Warned that delivery may not be available
- May need to arrange pickup from nearby areas

**Scenarios:**

#### Scenario 1: Chefs available locally
```
Consumer in Dallas, TX (where Maria & Raj serve)
→ ✅ "Great! 2 chef(s) are serving in Dallas, TX."
→ Full service available
```

#### Scenario 2: No local chefs
```
Consumer in Austin, TX (no chefs yet)
→ ✅ "No chefs in Austin, TX yet. Here are nearby chefs:"
   • Maria Rodriguez in Dallas, TX
   • Raj Patel in Dallas, TX
→ ⚠️ "Delivery may not be available. You might need to pickup your order."
→ Can still signup and order
```

#### Scenario 3: No chefs anywhere
```
Consumer in Remote Area (first user ever)
→ ✅ "You can signup, but no chefs are available yet in your area."
→ ⚠️ "Be the first to encourage chefs in your area!"
→ Can signup, but limited ordering options
```

**Message shown:**
- With local chefs: *"Great! X chef(s) are serving in [City], [State]."*
- Without local chefs: *"No chefs in [City], [State] yet. Here are nearby chefs: [List]"*
- Warning: *"Delivery may not be available. You might need to pickup your order."*

---

### 🚗 **DELIVERY AGENTS**
**Can signup: ONLY where chefs exist** ⚠️

- **Restricted to areas with active chefs**
- Delivery agents support existing chef operations
- Cannot signup in areas without chefs
- Must have at least 1 active chef in the city/state

**Scenarios:**

#### Scenario 1: Chefs available
```
Delivery Agent in Dallas, TX (Maria & Raj serve here)
→ ✅ "Great! 2 chef(s) are serving in Dallas, TX."
→ "You can start delivering orders in this area!"
```

#### Scenario 2: No chefs
```
Delivery Agent in Austin, TX (no chefs)
→ ❌ "No chefs are serving in this area yet."
→ "Delivery agents can only signup in areas with active chefs."
→ SIGNUP BLOCKED
```

**Message shown:**
- With chefs: *"Great! X chef(s) are serving in [City], [State]. You can start delivering orders!"*
- Without chefs: *"No chefs are serving in this area yet. Delivery agents can only signup in areas with active chefs."* (Signup blocked)

---

## 🔄 How Service Areas Expand

### Step-by-Step Expansion:

1. **Phase 1: Pioneer Chef**
   - First chef signs up in Tokyo, Japan
   - Tokyo becomes a new service area
   - Platform now operates in Tokyo

2. **Phase 2: Consumers Join**
   - Consumers in Tokyo can order from the chef
   - Consumers in nearby cities see Tokyo chef as "nearby"
   - Warning shown if delivery isn't available

3. **Phase 3: Delivery Agents**
   - Once chef exists, delivery agents can signup
   - Delivery agents enable full service experience
   - Orders can be delivered instead of pickup only

4. **Phase 4: Market Maturation**
   - More chefs join the area
   - More delivery agents join
   - Better coverage and options
   - Faster delivery times

---

## 🎯 Validation Logic

### Backend Check (Python)
```python
if user_type == 'chef':
    # Always allow
    return valid=True
    
elif user_type == 'delivery':
    # Check if chefs exist in city/state
    chefs = get_chefs_in_area(city, state)
    if chefs:
        return valid=True
    else:
        return valid=False, message="No chefs in area"
        
elif user_type == 'consumer':
    # Always allow, but warn if no local chefs
    chefs = get_chefs_in_area(city, state)
    if chefs:
        return valid=True, has_local_chefs=True
    else:
        nearest = find_nearest_chefs(city, state)
        return valid=True, has_local_chefs=False, nearest_chefs=nearest
```

### Database Query
```sql
-- Find chefs in specific city/state
SELECT * FROM users 
WHERE user_type = 'chef' 
AND is_active = 1 
AND city = ? AND state = ?

-- Find nearest chefs (if none local)
SELECT * FROM users 
WHERE user_type = 'chef' 
AND is_active = 1 
LIMIT 5
```

---

## 🧪 Testing Examples

### Test 1: Chef Pioneer
```
Role: Chef
Location: 75252 (Dallas, TX) - Already has chefs
Expected: ✅ "Welcome Chef! You can start serving in this area."
```

### Test 2: Chef in New City
```
Role: Chef
Location: 78701 (Austin, TX) - No chefs yet
Expected: ✅ "Welcome Chef! You can start serving in this area. You'll be pioneering food service in this area!"
```

### Test 3: Consumer with Local Chefs
```
Role: Consumer
Location: 75201 (Dallas, TX) - Has Maria & Raj
Expected: ✅ "Great! 2 chef(s) are serving in Dallas, TX."
```

### Test 4: Consumer without Local Chefs
```
Role: Consumer
Location: 78701 (Austin, TX) - No chefs
Expected: ✅ "No chefs in Austin, TX yet. Here are nearby chefs:"
         + List of Dallas chefs
         + Warning about delivery
```

### Test 5: Delivery Agent with Chefs
```
Role: Delivery Agent
Location: 75201 (Dallas, TX) - Has chefs
Expected: ✅ "Great! 2 chef(s) are serving in Dallas, TX. You can start delivering orders!"
```

### Test 6: Delivery Agent without Chefs
```
Role: Delivery Agent
Location: 78701 (Austin, TX) - No chefs
Expected: ❌ "No chefs are serving in this area yet. Delivery agents can only signup in areas with active chefs."
```

---

## 📊 Current Test Data

### Existing Chefs in Database:
1. **Maria Rodriguez** - Dallas, TX (Mexican food)
2. **Raj Patel** - Dallas, TX (Indian food)

### Service Areas:
- ✅ **Dallas, TX** - 2 active chefs

### Test Recommendations:
1. Test chef signup in Dallas (existing area)
2. Test chef signup in new city (e.g., Austin)
3. Test consumer signup in Dallas (should work)
4. Test consumer signup in Austin (should work with warning)
5. Test delivery agent in Dallas (should work)
6. Test delivery agent in Austin (should fail)

---

## 🚀 Future Enhancements

1. **Distance Calculation:**
   - Calculate actual distance between consumer and nearest chef
   - Show distance in miles/km
   - Estimate delivery fees based on distance

2. **Service Radius:**
   - Chefs can set their delivery radius
   - Show chefs within X miles of consumer
   - Filter by maximum distance

3. **Delivery Agent Range:**
   - Agents can set their operating radius
   - Match orders to agents in range
   - Optimize delivery assignments

4. **Multi-City Support:**
   - Support chefs serving multiple nearby cities
   - Regional service areas instead of city-specific
   - Metropolitan area coverage

---

**Updated:** October 13, 2025  
**Version:** 1.0  

