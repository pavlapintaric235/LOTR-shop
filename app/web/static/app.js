let accessToken = null;
let currentUser = null;
let allProducts = [];
let selectedCategorySlug = null;

const userStatusEl = document.getElementById("user-status");
const signoutButton = document.getElementById("signout-button");

const signupForm = document.getElementById("signup-form");
const signupMessageEl = document.getElementById("signup-message");

const loginForm = document.getElementById("login-form");
const loginMessageEl = document.getElementById("login-message");

const productsGridEl = document.getElementById("products-grid");
const productsTitleEl = document.getElementById("products-title");
const productsSubtitleEl = document.getElementById("products-subtitle");
const refreshProductsButton = document.getElementById("refresh-products-button");

const filterAllFeaturedButton = document.getElementById("filter-all-featured");
const slugFilterButtons = document.querySelectorAll(".slug-filter-button");

const cartItemsEl = document.getElementById("cart-items");
const cartTotalEl = document.getElementById("cart-total");
const cartMessageEl = document.getElementById("cart-message");
const refreshCartButton = document.getElementById("refresh-cart-button");
const checkoutButton = document.getElementById("checkout-button");

const ordersListEl = document.getElementById("orders-list");
const ordersMessageEl = document.getElementById("orders-message");
const refreshOrdersButton = document.getElementById("refresh-orders-button");

const adminSectionEl = document.getElementById("admin-section");
const adminOrdersListEl = document.getElementById("admin-orders-list");
const adminMessageEl = document.getElementById("admin-message");
const refreshAdminOrdersButton = document.getElementById("refresh-admin-orders-button");

function setMessage(element, message) {
    element.textContent = message ?? "";
}

function clearMessages() {
    setMessage(signupMessageEl, "");
    setMessage(loginMessageEl, "");
    setMessage(cartMessageEl, "");
    setMessage(ordersMessageEl, "");
    setMessage(adminMessageEl, "");
}

function formatPrice(value) {
    const numericValue = Number(value);
    return `€${numericValue.toFixed(2)}`;
}

function getAuthHeaders() {
    if (!accessToken) {
        return {};
    }

    return {
        Authorization: `Bearer ${accessToken}`,
    };
}

function updateAuthUi() {
    if (currentUser) {
        userStatusEl.textContent = `Signed in as ${currentUser.username}`;
        signoutButton.classList.remove("hidden");
    } else {
        userStatusEl.textContent = "Not signed in";
        signoutButton.classList.add("hidden");
    }

    if (currentUser?.is_admin) {
        adminSectionEl.classList.remove("hidden");
    } else {
        adminSectionEl.classList.add("hidden");
    }
}

async function parseResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    const rawText = await response.text();

    if (!rawText) {
        return null;
    }

    if (contentType.includes("application/json")) {
        try {
            return JSON.parse(rawText);
        } catch {
            return rawText;
        }
    }

    return rawText;
}

async function apiRequest(path, options = {}) {
    const response = await fetch(path, {
        ...options,
        headers: {
            ...(options.headers || {}),
            ...getAuthHeaders(),
        },
    });

    if (response.status === 204) {
        return null;
    }

    const data = await parseResponse(response);

    if (!response.ok) {
        if (typeof data === "string") {
            throw new Error(data);
        }

        if (data && typeof data.detail === "string") {
            throw new Error(data.detail);
        }

        if (data && data.detail) {
            throw new Error(JSON.stringify(data.detail));
        }

        throw new Error(`Request failed with status ${response.status}`);
    }

    return data;
}

function getFeaturedProducts(products) {
    return products.filter((product) => product.is_featured);
}

function getVisibleProducts() {
    if (!selectedCategorySlug) {
        return getFeaturedProducts(allProducts);
    }

    return allProducts.filter(
        (product) => product.category.slug === selectedCategorySlug
    );
}

function updateProductsHeader() {
    if (!selectedCategorySlug) {
        productsTitleEl.textContent = "Featured Products";
        productsSubtitleEl.textContent = "Highlighted picks from the shop.";
    } else {
        productsTitleEl.textContent = selectedCategorySlug;
        productsSubtitleEl.textContent = `All products in ${selectedCategorySlug}.`;
    }
}

function updateFilterButtonState() {
    filterAllFeaturedButton.classList.toggle("active-filter", selectedCategorySlug === null);

    slugFilterButtons.forEach((button) => {
        button.classList.toggle("active-filter", button.dataset.slug === selectedCategorySlug);
    });
}

function renderProducts(products) {
    updateProductsHeader();

    if (!products.length) {
        productsGridEl.innerHTML = "<p>No products found for this category.</p>";
        return;
    }

    productsGridEl.innerHTML = products.map((product) => `
        <div class="product-card">
            ${product.image_url ? `<img src="${product.image_url}" alt="${product.name}" class="product-image">` : ""}
            <div class="product-badges">
                ${product.is_featured ? `<span class="badge">Featured</span>` : ""}
                ${product.stock > 0 ? `<span class="badge badge-stock">In stock</span>` : `<span class="badge badge-out">Out of stock</span>`}
            </div>
            <h3>${product.name}</h3>
            <div class="product-meta">
                <div>Category: ${product.category.name}</div>
                <div>Category slug: ${product.category.slug}</div>
                <div>Price: ${formatPrice(product.price)}</div>
                <div>Stock: ${product.stock}</div>
            </div>
            <p>${product.description ?? ""}</p>
            <button data-product-id="${product.id}" class="add-to-cart-button" type="button" ${product.stock < 1 ? "disabled" : ""}>
                Add to cart
            </button>
        </div>
    `).join("");

    document.querySelectorAll(".add-to-cart-button").forEach((button) => {
        button.addEventListener("click", async () => {
            if (!accessToken) {
                setMessage(cartMessageEl, "You need to log in first.");
                return;
            }

            const productId = Number(button.dataset.productId);

            try {
                setMessage(cartMessageEl, "");
                await apiRequest("/cart/items", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ product_id: productId, quantity: 1 }),
                });
                await loadCart();
                setMessage(cartMessageEl, "Item added to cart.");
            } catch (error) {
                setMessage(cartMessageEl, error.message);
            }
        });
    });
}

function renderCart(cart) {
    const items = cart.items ?? [];

    if (!items.length) {
        cartItemsEl.innerHTML = "<p>Cart is empty.</p>";
        cartTotalEl.textContent = "€0.00";
        checkoutButton.disabled = true;
        return;
    }

    checkoutButton.disabled = false;

    cartItemsEl.innerHTML = items.map((item) => `
        <div class="cart-item">
            <div class="cart-item-main">
                <strong>${item.product.name}</strong>
                <div>Unit price: ${formatPrice(item.product.price)}</div>
                <div>Subtotal: ${formatPrice(item.subtotal)}</div>
            </div>
            <div class="cart-item-actions">
                <label class="compact-label">
                    Qty
                    <input type="number" min="1" value="${item.quantity}" class="cart-quantity-input" data-item-id="${item.id}">
                </label>
                <button type="button" class="secondary-button update-cart-item-button" data-item-id="${item.id}">
                    Update
                </button>
                <button type="button" class="danger-button remove-cart-item-button" data-item-id="${item.id}">
                    Remove
                </button>
            </div>
        </div>
    `).join("");

    cartTotalEl.textContent = formatPrice(cart.total);

    document.querySelectorAll(".update-cart-item-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const itemId = Number(button.dataset.itemId);
            const input = document.querySelector(`.cart-quantity-input[data-item-id="${itemId}"]`);
            const quantity = Number(input.value);

            try {
                await apiRequest(`/cart/items/${itemId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ quantity }),
                });
                await loadCart();
                setMessage(cartMessageEl, "Cart updated.");
            } catch (error) {
                setMessage(cartMessageEl, error.message);
            }
        });
    });

    document.querySelectorAll(".remove-cart-item-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const itemId = Number(button.dataset.itemId);

            try {
                await apiRequest(`/cart/items/${itemId}`, {
                    method: "DELETE",
                });
                await loadCart();
                setMessage(cartMessageEl, "Item removed.");
            } catch (error) {
                setMessage(cartMessageEl, error.message);
            }
        });
    });
}

function renderOrders(orders) {
    if (!orders.length) {
        ordersListEl.innerHTML = "<p>No orders yet.</p>";
        return;
    }

    ordersListEl.innerHTML = orders.map((order) => `
        <div class="order-card">
            <h3>Order #${order.id}</h3>
            <div>Status: ${order.status}</div>
            <div>Payment: ${order.payment_status}</div>
            <div>Total: ${formatPrice(order.total_amount)}</div>
            <div>Items: ${order.items.length}</div>
            <div class="order-actions">
                ${order.payment_status !== "paid" ? `
                    <button type="button" class="pay-order-button" data-order-id="${order.id}">
                        Pay now
                    </button>
                ` : ""}
                <button type="button" class="secondary-button refresh-payment-button" data-order-id="${order.id}">
                    Refresh payment
                </button>
            </div>
        </div>
    `).join("");

    document.querySelectorAll(".pay-order-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const orderId = Number(button.dataset.orderId);

            try {
                await apiRequest(`/payments/orders/${orderId}/pay`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ simulate_status: "success" }),
                });
                await loadOrders();
                if (currentUser?.is_admin) {
                    await loadAdminOrders();
                }
                setMessage(ordersMessageEl, "Payment completed.");
            } catch (error) {
                setMessage(ordersMessageEl, error.message);
            }
        });
    });

    document.querySelectorAll(".refresh-payment-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const orderId = Number(button.dataset.orderId);

            try {
                const payment = await apiRequest(`/payments/orders/${orderId}`);
                setMessage(
                    ordersMessageEl,
                    `Order #${payment.order_id}: payment=${payment.payment_status}, order=${payment.order_status}`
                );
                await loadOrders();
            } catch (error) {
                setMessage(ordersMessageEl, error.message);
            }
        });
    });
}

function renderAdminOrders(orders) {
    if (!orders.length) {
        adminOrdersListEl.innerHTML = "<p>No orders found.</p>";
        return;
    }

    const allowedStatuses = ["processing", "shipped", "delivered", "cancelled"];

    adminOrdersListEl.innerHTML = orders.map((order) => `
        <div class="order-card">
            <h3>Order #${order.id}</h3>
            <div>Status: ${order.status}</div>
            <div>Payment: ${order.payment_status}</div>
            <div>Total: ${formatPrice(order.total_amount)}</div>
            <div>Items: ${order.items.length}</div>
            <div class="admin-status-row">
                <select class="admin-status-select" data-order-id="${order.id}">
                    ${allowedStatuses.map((status) => `
                        <option value="${status}" ${status === order.status ? "selected" : ""}>${status}</option>
                    `).join("")}
                </select>
                <button type="button" class="secondary-button update-admin-status-button" data-order-id="${order.id}">
                    Update status
                </button>
            </div>
        </div>
    `).join("");

    document.querySelectorAll(".update-admin-status-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const orderId = Number(button.dataset.orderId);
            const select = document.querySelector(`.admin-status-select[data-order-id="${orderId}"]`);
            const status = select.value;

            try {
                await apiRequest(`/admin/orders/${orderId}/status`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status }),
                });
                await loadAdminOrders();
                await loadOrders();
                setMessage(adminMessageEl, "Order status updated.");
            } catch (error) {
                setMessage(adminMessageEl, error.message);
            }
        });
    });
}

async function loadProducts() {
    const products = await apiRequest("/products");
    allProducts = products;
    updateFilterButtonState();
    renderProducts(getVisibleProducts());
}

async function loadCart() {
    if (!accessToken) {
        cartItemsEl.innerHTML = "<p>Log in to see your cart.</p>";
        cartTotalEl.textContent = "€0.00";
        checkoutButton.disabled = true;
        return;
    }

    const cart = await apiRequest("/cart");
    renderCart(cart);
}

async function loadOrders() {
    if (!accessToken) {
        ordersListEl.innerHTML = "<p>Log in to see your orders.</p>";
        return;
    }

    const orders = await apiRequest("/orders");
    renderOrders(orders);
}

async function loadAdminOrders() {
    if (!currentUser?.is_admin) {
        adminOrdersListEl.innerHTML = "";
        return;
    }

    const orders = await apiRequest("/admin/orders");
    renderAdminOrders(orders);
}

async function loadCurrentUser() {
    if (!accessToken) {
        currentUser = null;
        updateAuthUi();
        return null;
    }

    try {
        currentUser = await apiRequest("/users/me");
        updateAuthUi();
        return currentUser;
    } catch (error) {
        accessToken = null;
        currentUser = null;
        updateAuthUi();
        setMessage(loginMessageEl, "Session expired. Please log in again.");
        return null;
    }
}

signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();

    const email = document.getElementById("signup-email").value.trim();
    const username = document.getElementById("signup-username").value.trim();
    const password = document.getElementById("signup-password").value;

    try {
        await apiRequest("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, password }),
        });

        setMessage(signupMessageEl, "Account created. You can log in now.");
        signupForm.reset();
    } catch (error) {
        setMessage(signupMessageEl, error.message);
    }
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch("/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username, password }),
        });

        const data = await parseResponse(response);

        if (!response.ok) {
            if (typeof data === "string") {
                throw new Error(data);
            }
            throw new Error(data?.detail ?? "Log in failed");
        }

        accessToken = data.access_token;

        await loadCurrentUser();
        await loadCart();
        await loadOrders();
        await loadAdminOrders();

        setMessage(loginMessageEl, "Log in successful.");
    } catch (error) {
        setMessage(loginMessageEl, error.message);
    }
});

signoutButton.addEventListener("click", async () => {
    accessToken = null;
    currentUser = null;
    updateAuthUi();
    cartItemsEl.innerHTML = "<p>Log in to see your cart.</p>";
    ordersListEl.innerHTML = "<p>Log in to see your orders.</p>";
    adminOrdersListEl.innerHTML = "";
    cartTotalEl.textContent = "€0.00";
    checkoutButton.disabled = true;
    clearMessages();
    setMessage(loginMessageEl, "Signed out.");
});

refreshProductsButton.addEventListener("click", async () => {
    try {
        await loadProducts();
    } catch (error) {
        setMessage(loginMessageEl, error.message);
    }
});

filterAllFeaturedButton.addEventListener("click", () => {
    selectedCategorySlug = null;
    updateFilterButtonState();
    renderProducts(getVisibleProducts());
});

slugFilterButtons.forEach((button) => {
    button.addEventListener("click", () => {
        selectedCategorySlug = button.dataset.slug;
        updateFilterButtonState();
        renderProducts(getVisibleProducts());
    });
});

refreshCartButton.addEventListener("click", async () => {
    try {
        await loadCart();
        setMessage(cartMessageEl, "");
    } catch (error) {
        setMessage(cartMessageEl, error.message);
    }
});

refreshOrdersButton.addEventListener("click", async () => {
    try {
        await loadOrders();
        setMessage(ordersMessageEl, "");
    } catch (error) {
        setMessage(ordersMessageEl, error.message);
    }
});

refreshAdminOrdersButton.addEventListener("click", async () => {
    try {
        await loadAdminOrders();
        setMessage(adminMessageEl, "");
    } catch (error) {
        setMessage(adminMessageEl, error.message);
    }
});

checkoutButton.addEventListener("click", async () => {
    if (!accessToken) {
        setMessage(cartMessageEl, "You need to log in first.");
        return;
    }

    try {
        setMessage(cartMessageEl, "");
        await apiRequest("/orders/checkout", {
            method: "POST",
        });
        await loadCart();
        await loadOrders();
        if (currentUser?.is_admin) {
            await loadAdminOrders();
        }
        setMessage(cartMessageEl, "Checkout successful.");
    } catch (error) {
        setMessage(cartMessageEl, error.message);
    }
});

(async function bootstrap() {
    await loadProducts();
    await loadCurrentUser();
    await loadCart();
    await loadOrders();
    await loadAdminOrders();
})();