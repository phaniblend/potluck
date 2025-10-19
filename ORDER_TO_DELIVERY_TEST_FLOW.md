# Order to Delivery Test Flow

## Test Environment Setup
- **Backend Server**: Running on `http://localhost:5000`
- **Test ZIP Code**: `75001` (Dallas, TX)
- **All test users are in the same service area for this flow**

---

## Test Users (from seed_test_data.py)

### 👤 Consumer
- **Email**: `john.doe@email.com`
- **Password**: `password123`
- **Name**: John Doe
- **Role**: Consumer

### 👨‍🍳 Chef
- **Email**: `maria.chef@email.com`
- **Password**: `password123`
- **Name**: Maria Garcia
- **Role**: Chef
- **Service Area**: 75001 (Dallas, TX)

### 🚗 Delivery Agent
- **Email**: `mike.driver@email.com`
- **Password**: `password123`
- **Name**: Mike Wilson
- **Role**: Delivery Agent

---

## 🔄 Complete Test Flow

### **STEP 1: Consumer - Browse and Place Order**

1. **Login as Consumer**
   - Navigate to: `http://localhost:5000`
   - Email: `john.doe@email.com`
   - Password: `password123`
   - Click "Login"
   - ✅ **Expected**: Redirected to `/pages/consumer-dashboard.html`

2. **Browse Available Dishes**
   - ✅ **Expected**: See 9 dishes from Maria Garcia's kitchen
   - Dishes include: Tacos al Pastor, Chicken Tikka Masala, Pad Thai, etc.
   - Each dish shows: Name, Price, Chef name, Rating

3. **Add Items to Cart**
   - Click "Add to Cart" on **"Tacos al Pastor"** ($12.99)
   - Click "Add to Cart" on **"Chicken Tikka Masala"** ($14.99)
   - ✅ **Expected**: Cart badge shows "2"
   - ✅ **Expected**: Green toast notification appears

4. **Review Cart**
   - Click the 🛒 cart icon in header
   - ✅ **Expected**: Cart sidebar opens showing 2 items
   - ✅ **Expected**: Total shows $27.98

5. **Proceed to Checkout**
   - Click "Proceed to Checkout" button
   - ✅ **Expected**: Checkout modal opens

6. **Enter Delivery Details**
   - **Delivery Address**: `123 Main St, Dallas, TX 75001`
   - **Phone**: `214-555-0100`
   - **Delivery Type**: Select "Delivery" (not Pickup)
   - **Special Instructions**: `Please ring the doorbell`

7. **Place Order**
   - Click "Place Order" button
   - ✅ **Expected**: Success toast "Order placed successfully!"
   - ✅ **Expected**: Redirected to "My Orders" tab
   - ✅ **Expected**: Order appears with status "pending"
   - **📝 Note the Order ID** (e.g., Order #1)

8. **Verify Order Details**
   - Click "View Details" on the order
   - ✅ **Expected**: Order shows:
     - Status: Pending
     - Items: Tacos al Pastor, Chicken Tikka Masala
     - Total: $27.98
     - Delivery address
     - Chef: Maria Garcia

9. **Logout**
   - Click user menu → Logout

---

### **STEP 2: Chef - Accept and Prepare Order**

1. **Login as Chef**
   - Navigate to: `http://localhost:5000`
   - Email: `maria.chef@email.com`
   - Password: `password123`
   - Click "Login"
   - ✅ **Expected**: Redirected to `/pages/chef-dashboard.html`

2. **View New Order Notification**
   - ✅ **Expected**: Notification badge shows "1"
   - ✅ **Expected**: Dashboard shows "Active Orders: 1"

3. **Go to Orders Tab**
   - Click "📦 Orders" tab
   - ✅ **Expected**: See the order from John Doe
   - ✅ **Expected**: Order status is "pending"

4. **View Order Details**
   - Click "View Details" on the order
   - ✅ **Expected**: Modal shows:
     - Customer: John Doe
     - Items: Tacos al Pastor, Chicken Tikka Masala
     - Total: $27.98
     - Delivery address: 123 Main St, Dallas, TX 75001
     - Special instructions: "Please ring the doorbell"

5. **Accept Order**
   - Click "Accept Order" button
   - ✅ **Expected**: Success toast "Order accepted!"
   - ✅ **Expected**: Order status changes to "accepted"

6. **Start Preparing**
   - Click "Start Preparing" button
   - ✅ **Expected**: Success toast "Order preparation started!"
   - ✅ **Expected**: Order status changes to "preparing"
   - ✅ **Expected**: Timer starts showing preparation time

7. **Mark as Ready**
   - After reviewing the order, click "Mark as Ready" button
   - ✅ **Expected**: Success toast "Order marked as ready!"
   - ✅ **Expected**: Order status changes to "ready_for_pickup"
   - ✅ **Expected**: Order moves to "Ready for Pickup" section

8. **Verify Order is Ready for Pickup**
   - ✅ **Expected**: Order shows in "Ready for Pickup" section
   - ✅ **Expected**: Waiting for delivery agent to pick up

9. **Logout**
   - Click user menu → Logout

---

### **STEP 3: Delivery Agent - Pick Up and Deliver**

1. **Login as Delivery Agent**
   - Navigate to: `http://localhost:5000`
   - Email: `mike.driver@email.com`
   - Password: `password123`
   - Click "Login"
   - ✅ **Expected**: Redirected to `/pages/delivery-dashboard.html`

2. **Set Service Area (if not already set)**
   - If no service area is set:
     - Click "Add Service Area" button
     - Enter ZIP: `75001`
     - Enter City: `Dallas`
     - Enter State: `TX`
     - Enter Country: `United States`
     - Click "Save"
   - ✅ **Expected**: Service area saved successfully

3. **View Available Jobs**
   - Go to "Available Jobs" section
   - ✅ **Expected**: See the order from John Doe
   - ✅ **Expected**: Order shows:
     - Pickup: Maria Garcia's location
     - Delivery: 123 Main St, Dallas, TX 75001
     - Estimated earnings: ~$5-8
     - Distance: calculated

4. **Accept Delivery Job**
   - Click "Accept Job" button
   - ✅ **Expected**: Success toast "Job accepted!"
   - ✅ **Expected**: Order moves to "Active Deliveries" section
   - ✅ **Expected**: Status changes to "assigned"

5. **Navigate to Pickup Location**
   - Click "Navigate to Pickup" button
   - ✅ **Expected**: Opens map/navigation to chef's location
   - (In real scenario, driver would physically go to pickup)

6. **Mark as Picked Up**
   - Click "Picked Up" button
   - ✅ **Expected**: Success toast "Order picked up!"
   - ✅ **Expected**: Order status changes to "picked_up"
   - ✅ **Expected**: "Navigate to Customer" button appears

7. **Navigate to Customer**
   - Click "Navigate to Customer" button
   - ✅ **Expected**: Opens map/navigation to customer's address
   - (In real scenario, driver would physically deliver)

8. **Mark as Delivered**
   - Click "Delivered" button
   - ✅ **Expected**: Success toast "Order delivered!"
   - ✅ **Expected**: Order status changes to "delivered"
   - ✅ **Expected**: Order moves to "Completed Deliveries" section
   - ✅ **Expected**: Earnings updated

9. **View Earnings**
   - Check "Today's Earnings" section
   - ✅ **Expected**: Shows earnings from this delivery
   - ✅ **Expected**: Total deliveries count increased

10. **Logout**
    - Click user menu → Logout

---

### **STEP 4: Consumer - Rate and Review**

1. **Login as Consumer Again**
   - Navigate to: `http://localhost:5000`
   - Email: `john.doe@email.com`
   - Password: `password123`
   - Click "Login"

2. **Check Order Status**
   - Go to "My Orders" tab
   - ✅ **Expected**: Order status is "delivered"
   - ✅ **Expected**: "Rate Order" button appears

3. **View Order History**
   - Go to "📜 Order History" tab
   - ✅ **Expected**: Completed order appears in history
   - ✅ **Expected**: Shows all order details

4. **Rate the Order**
   - Click "Rate Order" button
   - ✅ **Expected**: Rating modal opens

5. **Submit Ratings**
   - **Food Rating**: Select 5 stars ⭐⭐⭐⭐⭐
   - **Chef Rating**: Select 5 stars ⭐⭐⭐⭐⭐
   - **Delivery Rating**: Select 5 stars ⭐⭐⭐⭐⭐
   - **Tip**: Select $5.00
   - **Review**: "Amazing food! Fast delivery!"
   - Click "Submit Rating"
   - ✅ **Expected**: Success toast "Thank you for your feedback!"
   - ✅ **Expected**: Rating modal closes
   - ✅ **Expected**: Order shows as rated

6. **Test Repeat Order**
   - Click "🔄 Repeat Last Order" button
   - ✅ **Expected**: Cart opens with same items
   - ✅ **Expected**: 2 items in cart (Tacos, Tikka Masala)

7. **Test Favorites**
   - Go to "Browse Food" tab
   - Click ❤️ icon on "Pad Thai" dish
   - ✅ **Expected**: Success toast "Added to favorites!"
   - Go to "❤️ Favorites" tab
   - ✅ **Expected**: Pad Thai appears in favorites
   - Click "Add to Cart" from favorites
   - ✅ **Expected**: Item added to cart

8. **Logout**

---

## 🎯 Success Criteria

### Consumer Dashboard
- ✅ Can browse dishes from chefs in service area
- ✅ Can add/remove items from cart
- ✅ Can place orders with delivery details
- ✅ Can view order status in real-time
- ✅ Can rate completed orders
- ✅ Can add dishes to favorites
- ✅ Can repeat previous orders
- ✅ Receives notifications for order updates

### Chef Dashboard
- ✅ Receives new order notifications
- ✅ Can view order details
- ✅ Can accept/reject orders
- ✅ Can update order status (preparing → ready)
- ✅ Can track active orders
- ✅ Can view order history
- ✅ Earnings updated after completed orders

### Delivery Dashboard
- ✅ Can set service area
- ✅ Can view available jobs in service area
- ✅ Can accept delivery jobs
- ✅ Can navigate to pickup/delivery locations
- ✅ Can update delivery status
- ✅ Can view earnings
- ✅ Can track completed deliveries

---

## 🐛 Common Issues to Check

1. **Order not appearing for chef**
   - Check if chef's service area matches consumer's delivery address ZIP
   - Verify order status in database

2. **Delivery job not appearing**
   - Check if delivery agent has set service area to 75001
   - Verify order status is "ready_for_pickup"

3. **Status not updating**
   - Check browser console for errors
   - Verify WebSocket connection (if implemented)
   - Hard refresh browser (Ctrl+Shift+R)

4. **Cart not working**
   - Clear browser cache and localStorage
   - Check console for JavaScript errors

5. **Images not loading**
   - This is expected - we're using emoji placeholders
   - No action needed

---

## 📊 Database Verification (Optional)

After completing the flow, you can verify in the database:

```bash
cd potluck/backend
sqlite3 potluck.db

# Check order
SELECT * FROM orders WHERE consumer_id = 1;

# Check order items
SELECT * FROM order_items WHERE order_id = 1;

# Check ratings
SELECT * FROM ratings WHERE order_id = 1;

# Check delivery
SELECT * FROM deliveries WHERE order_id = 1;
```

---

## 🔄 Next Steps

After successful test:
1. Test edge cases (order rejection, cancellation)
2. Test multiple concurrent orders
3. Test different service areas
4. Test real-time notifications
5. Test payment integration (if implemented)
6. Test different dietary filters
7. Test search functionality

---

## 📝 Notes

- All test users have password: `password123`
- Test data includes 9 dishes from Maria Garcia
- Service area is set to Dallas, TX 75001
- Prices are in USD
- Ratings are on a 5-star scale
- Tips are optional but encouraged

**Happy Testing! 🎉**

