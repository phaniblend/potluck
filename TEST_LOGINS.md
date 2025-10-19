# 🔐 Test Login Credentials

## Quick Reference for Testing

All test accounts use the same password: **`password123`**

---

## 👤 Consumer Account
```
Email:    john.doe@email.com
Password: password123
Name:     John Doe
Role:     Consumer
ZIP:      75001 (Dallas, TX)
```

**Use this to:**
- Browse dishes
- Add items to cart
- Place orders
- Track deliveries
- Rate food/chef/delivery
- Manage favorites

---

## 👨‍🍳 Chef Account
```
Email:    maria.chef@email.com
Password: password123
Name:     Maria Garcia
Role:     Chef
ZIP:      75001 (Dallas, TX)
```

**Use this to:**
- View incoming orders
- Accept/reject orders
- Prepare orders
- Mark orders as ready
- Manage menu (9 dishes available)
- View earnings

---

## 🚗 Delivery Agent Account
```
Email:    mike.driver@email.com
Password: password123
Name:     Mike Wilson
Role:     Delivery Agent
ZIP:      Need to set to 75001
```

**Use this to:**
- Set service area (75001)
- View available delivery jobs
- Accept delivery jobs
- Pick up orders
- Deliver orders
- Track earnings

---

## 🌐 Login URL
```
http://localhost:5000
```

---

## 📋 Quick Test Sequence

### 1️⃣ Login as Consumer
```
john.doe@email.com / password123
```
→ Place an order

### 2️⃣ Login as Chef
```
maria.chef@email.com / password123
```
→ Accept and prepare the order

### 3️⃣ Login as Delivery Agent
```
mike.driver@email.com / password123
```
→ Pick up and deliver the order

### 4️⃣ Login as Consumer Again
```
john.doe@email.com / password123
```
→ Rate the order

---

## 🗄️ Database Location
```
potluck/backend/potluck.db
```

---

## 🔄 Reset Test Data
If you need to reset the test data:
```bash
cd potluck
python database/seed_test_data.py
```

---

## 📝 Notes
- All users are in the same service area (75001 - Dallas, TX)
- Chef has 9 pre-seeded dishes available
- Delivery agent needs to set service area on first login
- All passwords are hashed using bcrypt
- Test data includes various cuisines: Mexican, Indian, Thai, Italian, Japanese, Chinese

---

## 🎯 Test Scenarios

### Scenario 1: Basic Order Flow
1. Consumer: john.doe@email.com → Order Tacos ($12.99)
2. Chef: maria.chef@email.com → Accept & prepare
3. Delivery: mike.driver@email.com → Pick up & deliver
4. Consumer: john.doe@email.com → Rate 5 stars

### Scenario 2: Multiple Items
1. Consumer: Add Tacos + Tikka Masala ($27.98)
2. Test cart functionality
3. Complete full delivery flow

### Scenario 3: Favorites
1. Consumer: Add dishes to favorites
2. Order from favorites
3. Test repeat last order

---

## 🚨 Troubleshooting

**Can't login?**
- Make sure backend is running: `cd potluck/backend && python app.py`
- Check if test data is seeded: `python database/seed_test_data.py`
- Verify email is exact (case-sensitive)

**Wrong dashboard?**
- Clear browser localStorage
- Hard refresh (Ctrl+Shift+R)
- Check user role in database

**No dishes showing?**
- Verify chef and consumer are in same ZIP (75001)
- Check if dishes are active in database
- Refresh the page

---

**Happy Testing! 🎉**

