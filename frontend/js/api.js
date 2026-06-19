const BASE = 'http://127.0.0.1:8000/api';

// Token helpers
function getToken() { return localStorage.getItem('access_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('user') || 'null'); }

function saveAuth(data) {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
}

function clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
}

function parseJwt(token) {
    try {
        const payload = token.split('.')[1];
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
        const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
        return JSON.parse(atob(padded));
    } catch (error) {
        return null;
    }
}

function isTokenExpired(token) {
    const payload = parseJwt(token);
    return !payload || (payload.exp ? payload.exp * 1000 < Date.now() : true);
}

function isLoggedIn() {
    const token = getToken();
    return !!token && !isTokenExpired(token);
}

function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
    };
}

// Auth
async function register(username, email, password, phone) {
    const res = await fetch(`${BASE}/users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, phone })
    });
    return res.json();
}

async function login(username, password) {
    const res = await fetch(`${BASE}/users/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.access) saveAuth(data);
    return data;
}

// Products
async function getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    try {
        const res = await fetch(`${BASE}/products/?${query}`);
        if (!res.ok) {
            console.error('Products API error:', res.status, res.statusText);
            return [];
        }
        const data = await res.json();
        console.log('Products loaded:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch products:', error);
        return [];
    }
}

async function getProduct(slug) {
    try {
        const res = await fetch(`${BASE}/products/${slug}/`);
        if (!res.ok) {
            console.error('Product API error:', res.status, res.statusText);
            return { detail: 'Not found.' };
        }
        return res.json();
    } catch (error) {
        console.error('Failed to fetch product:', error);
        return { detail: 'Not found.' };
    }
}

async function getCategories() {
    try {
        const res = await fetch(`${BASE}/products/categories/`);
        if (!res.ok) {
            console.error('Categories API error:', res.status, res.statusText);
            return [];
        }
        const data = await res.json();
        console.log('Categories loaded:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch categories:', error);
        return [];
    }
}

// Cart
async function getCart() {
    const res = await fetch(`${BASE}/cart/`, { headers: authHeaders() });
    return res.json();
}

async function addToCart(product_id, quantity = 1) {
    const res = await fetch(`${BASE}/cart/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ product_id, quantity })
    });
    return res.json();
}

async function updateCartItem(item_id, quantity) {
    const res = await fetch(`${BASE}/cart/item/${item_id}/`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify({ quantity })
    });
    return res.json();
}

async function removeCartItem(item_id) {
    const res = await fetch(`${BASE}/cart/item/${item_id}/`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    return res.json();
}

async function clearCart() {
    const res = await fetch(`${BASE}/cart/`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    return res.json();
}

// Orders
async function placeOrder(shipping_address) {
    const res = await fetch(`${BASE}/orders/place/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ shipping_address })
    });
    return res.json();
}

async function getOrders() {
    const res = await fetch(`${BASE}/orders/`, { headers: authHeaders() });
    return res.json();
}

async function getOrder(order_id) {
    const res = await fetch(`${BASE}/orders/${order_id}/`, { headers: authHeaders() });
    return res.json();
}

async function cancelOrder(order_id) {
    const res = await fetch(`${BASE}/orders/${order_id}/cancel/`, {
        method: 'POST',
        headers: authHeaders()
    });
    return res.json();
}

// Wishlist
async function getWishlist() {
    const res = await fetch(`${BASE}/wishlist/`, { headers: authHeaders() });
    return res.json();
}

async function toggleWishlist(product_id) {
    const res = await fetch(`${BASE}/wishlist/toggle/${product_id}/`, {
        method: 'POST',
        headers: authHeaders()
    });
    return res.json();
}

async function getWishlistStatus(product_id) {
    const res = await fetch(`${BASE}/wishlist/status/${product_id}/`, {
        headers: authHeaders()
    });
    return res.json();
}