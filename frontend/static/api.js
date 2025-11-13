/**
 * Client API pour communiquer avec l'API Gateway
 */
const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    /**
     * Récupère le token depuis localStorage
     */
    getToken() {
        return localStorage.getItem('access_token');
    }

    /**
     * Sauvegarde le token dans localStorage
     */
    setToken(token) {
        localStorage.setItem('access_token', token);
    }

    /**
     * Supprime le token
     */
    clearToken() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    /**
     * Fait une requête HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Ajouter le token si disponible
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                // Si token expiré, rediriger vers login
                if (response.status === 401) {
                    this.clearToken();
                    window.location.href = '/login.html';
                    return null;
                }
                throw new Error(data.error?.message || 'Erreur de requête');
            }

            return data;
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    }

    /**
     * Login
     */
    async login(username, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (data && data.success) {
            this.setToken(data.data.access_token);
            localStorage.setItem('refresh_token', data.data.refresh_token);
            return data.data;
        }

        throw new Error('Échec de la connexion');
    }

    /**
     * Logout
     */
    async logout() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
            try {
                await this.request('/auth/logout', {
                    method: 'POST',
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
            } catch (error) {
                console.error('Erreur lors de la déconnexion:', error);
            }
        }
        this.clearToken();
    }

    /**
     * Récupère le profil utilisateur
     */
    async getProfile() {
        return await this.request('/users/profile');
    }

    /**
     * Récupère la liste des produits
     */
    async getProducts() {
        return await this.request('/products');
    }

    /**
     * Récupère un produit par ID
     */
    async getProduct(id) {
        return await this.request(`/products/${id}`);
    }

    /**
     * Récupère les commandes de l'utilisateur
     */
    async getOrders() {
        return await this.request('/orders');
    }

    /**
     * Crée une commande
     */
    async createOrder(items) {
        return await this.request('/orders', {
            method: 'POST',
            body: JSON.stringify({ items })
        });
    }
}

// Instance globale
const api = new APIClient();

