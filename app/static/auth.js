/**
 * Script de vérification du token JWT au chargement de la page
 * Vérifie si le token est valide et non expiré, redirige vers login si nécessaire
 */

(function() {
    'use strict';

    /**
     * Récupère le token JWT depuis localStorage
     */
    function getStoredToken() {
        return localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token');
    }

    /**
     * Supprime le token stocké
     */
    function clearStoredToken() {
        localStorage.removeItem('jwt_token');
        sessionStorage.removeItem('jwt_token');
    }

    /**
     * Vérifie la validité du token via l'API
     */
    async function verifyToken() {
        const token = getStoredToken();
        
        // Si pas de token stocké, on ne fait rien (l'utilisateur utilise peut-être les sessions Flask)
        if (!token) {
            return { valid: true, skip: true };
        }

        try {
            const response = await fetch('/auth/verify', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                }
            });

            const data = await response.json();

            if (!response.ok || !data.valid) {
                // Token invalide ou expiré
                clearStoredToken();
                
                // Afficher un message d'erreur si le token est expiré
                if (data.expired) {
                    alert('Votre session a expiré. Veuillez vous reconnecter.');
                }
                
                // Rediriger vers la page de login
                const currentPath = window.location.pathname;
                if (currentPath !== '/login' && !currentPath.startsWith('/login')) {
                    window.location.href = '/login';
                }
                
                return { valid: false, expired: data.expired || false };
            }

            return { valid: true, user: data.user };
        } catch (error) {
            console.error('Erreur lors de la vérification du token:', error);
            // En cas d'erreur réseau, on ne bloque pas l'utilisateur
            return { valid: true, error: true };
        }
    }

    /**
     * Initialise la vérification du token au chargement de la page
     */
    function initTokenVerification() {
        // Ne vérifier que si on n'est pas déjà sur la page de login
        const currentPath = window.location.pathname;
        if (currentPath === '/login' || currentPath.startsWith('/login')) {
            return;
        }

        // Vérifier le token au chargement de la page
        verifyToken().then(result => {
            if (!result.valid && !result.skip) {
                console.log('Token invalide ou expiré, redirection vers login');
            }
        });

        // Vérifier aussi lors du rafraîchissement de la page (événement beforeunload)
        window.addEventListener('beforeunload', function() {
            // Optionnel: on peut vérifier ici aussi
        });
    }

    // Attendre que le DOM soit chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTokenVerification);
    } else {
        initTokenVerification();
    }

    // Exposer les fonctions pour utilisation externe si nécessaire
    window.authUtils = {
        verifyToken: verifyToken,
        getStoredToken: getStoredToken,
        clearStoredToken: clearStoredToken
    };
})();

