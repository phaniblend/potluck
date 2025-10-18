# Potluck Testing Guide

## 🚀 Application is Running!

**Server URL:** http://localhost:5000  
**Frontend URL:** http://localhost:5000/  

---

## 📋 Sample Test Accounts

The database has been initialized with sample users for testing all three roles:

### 👤 Consumer Accounts
- **Email:** john@example.com  
  **Password:** password123  
  **Name:** John Doe  
  **Location:** Dallas, TX

- **Email:** jane@example.com  
  **Password:** password123  
  **Name:** Jane Smith  
  **Location:** Dallas, TX

### 👨‍🍳 Chef Accounts
- **Email:** maria@example.com  
  **Password:** password123  
  **Name:** Maria Rodriguez  
  **Specialties:** Mexican, Tex-Mex  
  **Rating:** 4.8⭐  
  **Available Dishes:** Chicken Tacos, Beef Enchiladas, Vegetarian Quesadilla

- **Email:** raj@example.com  
  **Password:** password123  
  **Name:** Raj Patel  
  **Specialties:** Indian, Vegetarian, Vegan  
  **Rating:** 4.9⭐  
  **Available Dishes:** Paneer Tikka Masala, Vegetable Biryani, Dal Tadka

### 🚗 Delivery Agent Accounts
- **Email:** mike@example.com  
  **Password:** password123  
  **Name:** Mike Wilson  
  **Vehicle:** Car  
  **Rating:** 4.7⭐  
  **Status:** Online

- **Email:** sarah@example.com  
  **Password:** password123  
  **Name:** Sarah Johnson  
  **Vehicle:** Scooter  
  **Rating:** 4.9⭐  
  **Status:** Online

---

## 🧪 Testing Steps

### Step 1: Access the Application
1. Open your browser
2. Navigate to: **http://localhost:5000**
3. You should see the Potluck login/signup page

### Important: Service Area Validation Rules 🌍

**Before testing, understand the signup rules:**

1. **👨‍🍳 CHEFS** → Can signup ANYWHERE (they create service areas)
2. **👤 CONSUMERS** → Can signup ANYWHERE (warned if no local chefs)
3. **🚗 DELIVERY AGENTS** → Can ONLY signup where chefs exist

See `SERVICE_AREA_RULES.md` for complete details.

### Step 2: Test Consumer Role
1. **Login** with john@example.com / password123
2. **Browse Available Dishes** from Maria and Raj
3. **View Dish Details** (ingredients, allergens, pricing)
4. **Add Items to Cart**
5. **Place an Order**
6. **Track Order Status**
7. **View Order History**
8. **Rate & Review** completed orders

### Step 3: Test Chef Role
1. **Logout** from consumer account
2. **Login** with maria@example.com / password123
3. **View Dashboard** (orders, earnings, stats)
4. **Manage Dishes:**
   - View existing dishes
   - Add new dish
   - Edit dish details
   - Set availability
5. **Manage Orders:**
   - Accept/reject incoming orders
   - Update order status (preparing, ready for pickup)
   - View order details
6. **Set Availability Schedule:**
   - Configure cooking hours
   - Set days available
7. **View Analytics:**
   - Total earnings
   - Popular dishes
   - Customer ratings

### Step 4: Test Delivery Agent Role
1. **Logout** from chef account
2. **Login** with mike@example.com / password123
3. **View Dashboard** (available deliveries, earnings)
4. **Toggle Online/Offline Status**
5. **Accept Delivery Requests**
6. **Update Delivery Status:**
   - Picked up from chef
   - Out for delivery
   - Delivered
7. **Track Earnings**
8. **View Delivery History**

### Step 5: Test Cross-Role Interactions
1. **Create an Order Flow:**
   - Consumer (John) places order for Maria's Chicken Tacos
   - Chef (Maria) receives and accepts order
   - Chef marks order as "ready for pickup"
   - Delivery Agent (Mike) accepts delivery
   - Mike picks up from Maria
   - Mike delivers to John
   - John confirms delivery and rates both Maria and Mike

---

## 🔍 API Endpoints to Test

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Authentication
- **POST** `/api/auth/signup` - Create new account
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/logout` - User logout
- **POST** `/api/auth/validate-location` - Check service area

### Consumer Endpoints
- **GET** `/api/dishes` - Browse available dishes
- **GET** `/api/dishes/:id` - Get dish details
- **POST** `/api/orders` - Place order
- **GET** `/api/orders/my-orders` - View order history
- **POST** `/api/reviews` - Submit review

### Chef Endpoints
- **GET** `/api/chef/dashboard` - Get chef stats
- **POST** `/api/chef/dishes` - Add new dish
- **PUT** `/api/chef/dishes/:id` - Update dish
- **DELETE** `/api/chef/dishes/:id` - Remove dish
- **GET** `/api/chef/orders` - View incoming orders
- **PUT** `/api/orders/:id/status` - Update order status

### Delivery Endpoints
- **GET** `/api/delivery/dashboard` - Get delivery stats
- **GET** `/api/delivery/available-orders` - View available deliveries
- **POST** `/api/delivery/accept/:order_id` - Accept delivery
- **PUT** `/api/delivery/status` - Update status (online/offline)
- **PUT** `/api/orders/:id/delivery-status` - Update delivery status

---

## 🎨 Features to Test

### User Experience
- [ ] Responsive design on mobile/tablet/desktop
- [ ] Smooth navigation between pages
- [ ] Real-time updates for order status
- [ ] Search and filter functionality
- [ ] Location-based service availability

### Consumer Features
- [ ] Browse dishes by cuisine, price, dietary preferences
- [ ] View chef profiles and ratings
- [ ] Add multiple items to cart
- [ ] Apply dietary filters (vegan, gluten-free, etc.)
- [ ] Save favorite chefs and dishes
- [ ] Order tracking with status updates
- [ ] Rate and review orders

### Chef Features
- [ ] Comprehensive dashboard with analytics
- [ ] Easy dish management (CRUD operations)
- [ ] Upload dish photos
- [ ] Set cooking schedule and availability
- [ ] Manage incoming orders
- [ ] View earnings and payout history
- [ ] Customer feedback and ratings

### Delivery Agent Features
- [ ] Real-time available deliveries
- [ ] Accept/decline delivery requests
- [ ] Navigation to pickup/delivery locations
- [ ] Update delivery status in real-time
- [ ] Track daily earnings
- [ ] View delivery history and ratings

### General Features
- [ ] Service area validation
- [ ] Secure authentication with JWT
- [ ] Password strength validation
- [ ] Email/phone uniqueness validation
- [ ] Error handling and user feedback
- [ ] Loading states and animations

---

## 🐛 Known Issues to Watch For

1. **Location Services:** Make sure location validation works for Dallas, TX
2. **Image Uploads:** Test image upload functionality for dish photos
3. **Real-time Updates:** WebSocket connections for live order tracking
4. **Payment Integration:** Currently using mock payment (future enhancement)

---

## 📝 Testing Checklist

### Authentication Flow
- [ ] Sign up as new consumer
- [ ] Sign up as new chef
- [ ] Sign up as new delivery agent
- [ ] Login with existing accounts
- [ ] Logout functionality
- [ ] Service area validation

### Consumer Flow
- [ ] Browse dishes
- [ ] Filter by cuisine/dietary preferences
- [ ] View dish details
- [ ] Add to cart
- [ ] Place order
- [ ] Track order status
- [ ] Receive order
- [ ] Rate and review

### Chef Flow
- [ ] View dashboard
- [ ] Add new dish
- [ ] Edit existing dish
- [ ] Set availability schedule
- [ ] Receive order notification
- [ ] Accept order
- [ ] Update cooking status
- [ ] Mark order ready
- [ ] View earnings

### Delivery Flow
- [ ] View available orders
- [ ] Accept delivery
- [ ] Update status to "picked up"
- [ ] Update status to "delivering"
- [ ] Complete delivery
- [ ] View earnings
- [ ] Toggle online/offline

---

## 🎯 Success Criteria

✅ All three roles can login successfully  
✅ Consumers can browse and order dishes  
✅ Chefs can manage dishes and accept orders  
✅ Delivery agents can accept and complete deliveries  
✅ Order flow works end-to-end  
✅ Ratings and reviews work  
✅ No critical errors in browser console  
✅ API endpoints respond correctly  
✅ UI is responsive and user-friendly  

---

## 📞 Need Help?

If you encounter any issues:
1. Check the browser console (F12) for JavaScript errors
2. Check the Flask terminal for backend errors
3. Verify the database exists: `E:\projects\PL-revamp\potluck\backend\potluck.db`
4. Ensure all dependencies are installed
5. Restart the server if needed

---

## 🔄 Restarting the Application

If you need to restart:
1. Stop the server: Press `Ctrl+C` in the terminal
2. Start again: `cd E:\projects\PL-revamp\potluck\backend && python app.py`

Or to reset the database:
```bash
cd E:\projects\PL-revamp\potluck
python database/init_db.py --with-data --force
```

---

**Happy Testing! 🎉**

