/**
 * Gestion du panier côté client (localStorage)
 */
class CartManager {
    constructor() {
        this.storageKey = 'shopping_cart';
    }

    /**
     * Récupère le panier depuis localStorage
     */
    getCart() {
        const cart = localStorage.getItem(this.storageKey);
        return cart ? JSON.parse(cart) : [];
    }

    /**
     * Sauvegarde le panier dans localStorage
     */
    saveCart(cart) {
        localStorage.setItem(this.storageKey, JSON.stringify(cart));
    }

    /**
     * Ajoute un produit au panier
     */
    addItem(product, quantity = 1) {
        const cart = this.getCart();
        const existingItem = cart.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            cart.push({
                id: product.id,
                name: product.name,
                price: product.price,
                description: product.description,
                quantity: quantity
            });
        }

        this.saveCart(cart);
        return cart;
    }

    /**
     * Supprime un produit du panier
     */
    removeItem(productId) {
        const cart = this.getCart();
        const filtered = cart.filter(item => item.id !== productId);
        this.saveCart(filtered);
        return filtered;
    }

    /**
     * Met à jour la quantité d'un produit
     */
    updateQuantity(productId, quantity) {
        const cart = this.getCart();
        const item = cart.find(item => item.id === productId);
        
        if (item) {
            if (quantity <= 0) {
                return this.removeItem(productId);
            }
            item.quantity = quantity;
            this.saveCart(cart);
        }
        
        return cart;
    }

    /**
     * Vide le panier
     */
    clear() {
        this.saveCart([]);
    }

    /**
     * Calcule le total du panier
     */
    getTotal() {
        const cart = this.getCart();
        return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    /**
     * Retourne le nombre d'articles dans le panier
     */
    getItemCount() {
        const cart = this.getCart();
        return cart.reduce((count, item) => count + item.quantity, 0);
    }
}

// Instance globale
const cartManager = new CartManager();

