/* ============================================================
   Plateforme — script global
   Bascule du mode nuit (classe « dark » sur <html>) avec
   préférence conservée dans localStorage.
   Le thème initial est appliqué AVANT le premier rendu
   (script inline dans <head> de base.html) pour éviter le flash.
   ============================================================ */

/* Bascule appelée par le(s) bouton(s) 🌙 / ☀️ de la barre de navigation */
function basculerTheme() {
    var sombre = document.documentElement.classList.toggle('dark');
    try {
        localStorage.setItem('theme', sombre ? 'dark' : 'light');
    } catch (e) { /* navigation privée : préférence non persistée */ }
    ['basculer_theme', 'basculer_theme_mobile'].forEach(function (id) {
        var bouton = document.getElementById(id);
        if (bouton) {
            bouton.textContent = sombre ? '☀️' : '🌙';
            bouton.title = sombre ? 'Passer en mode jour' : 'Passer en mode nuit';
        }
    });
}

/* ── Menu mobile : carte flottante ──
   Ouvre/ferme avec animation, met à jour l'icône hamburger ↔ ✕ */
var menuOuvert = false;

function basculerMenu() {
    menuOuvert ? fermerMenu() : ouvrirMenu();
}

function ouvrirMenu() {
    var menu = document.getElementById('menu_mobile');
    var bouton = document.getElementById('bouton_menu');
    var icone = document.getElementById('icone_menu');
    if (!menu || menuOuvert) return;
    menu.classList.remove('hidden', 'ferme');
    menuOuvert = true;
    if (bouton) {
        bouton.setAttribute('aria-expanded', 'true');
        bouton.setAttribute('aria-label', 'Fermer le menu');
    }
    if (icone) icone.setAttribute('d', 'M6 18L18 6M6 6l12 12');
}

function fermerMenu() {
    var menu = document.getElementById('menu_mobile');
    var bouton = document.getElementById('bouton_menu');
    var icone = document.getElementById('icone_menu');
    if (!menu || !menuOuvert) return;
    menuOuvert = false;
    menu.classList.add('ferme');
    setTimeout(function () { menu.classList.add('hidden'); menu.classList.remove('ferme'); }, 140);
    if (bouton) {
        bouton.setAttribute('aria-expanded', 'false');
        bouton.setAttribute('aria-label', 'Ouvrir le menu');
    }
    if (icone) icone.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
}

/* Au clic sur un lien du menu : navigation immédiate, pas besoin d'animer */
document.addEventListener('DOMContentLoaded', function () {
    var menu = document.getElementById('menu_mobile');
    if (!menu) return;
    menu.addEventListener('click', function (e) {
        var cible = e.target.closest('a');
        if (cible) { menu.classList.add('hidden'); menuOuvert = false; }
        else if (e.target.closest('button')) fermerMenu();
    });
});

/* Fermeture du menu au clic en dehors de la carte */
document.addEventListener('click', function (e) {
    if (!menuOuvert) return;
    var bouton = document.getElementById('bouton_menu');
    if (!e.target.closest('#menu_mobile') && e.target !== bouton && !bouton.contains(e.target)) fermerMenu();
});

/* Le menu n'a pas de sens en desktop : on le referme en repassant ≥ 768px */
window.addEventListener('resize', function () {
    if (window.innerWidth >= 768) menuOuvert = false;
    var menu = document.getElementById('menu_mobile');
    if (menu && window.innerWidth >= 768) {
        menu.classList.add('hidden');
        menu.classList.remove('ferme');
        var bouton = document.getElementById('bouton_menu');
        if (bouton) bouton.setAttribute('aria-expanded', 'false');
    }
}, { passive: true });

/* Met l'icône du bouton en accord avec le thème au chargement de chaque page */
document.addEventListener('DOMContentLoaded', function () {
    var sombre = document.documentElement.classList.contains('dark');
    ['basculer_theme', 'basculer_theme_mobile'].forEach(function (id) {
        var bouton = document.getElementById(id);
        if (bouton) {
            bouton.textContent = sombre ? '☀️' : '🌙';
            bouton.title = sombre ? 'Passer en mode jour' : 'Passer en mode nuit';
        }
    });
});

/* Navbar : ombre portée dès que la page est défilée */
window.addEventListener('scroll', function () {
    var nav = document.querySelector('nav');
    if (nav) nav.classList.toggle('ombre-defilement', window.scrollY > 8);
}, { passive: true });
