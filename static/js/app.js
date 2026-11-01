/* ============================================================
   Plateforme — script global
   Bascule du mode nuit (classe « dark » sur <html>) avec
   préférence conservée dans localStorage.
   Le thème initial est appliqué AVANT le premier rendu
   (script inline dans <head> de base.html) pour éviter le flash.
   ============================================================ */

/* Bascule appelée par le bouton 🌙 / ☀️ de la barre de navigation */
function basculerTheme() {
    var sombre = document.documentElement.classList.toggle('dark');
    try {
        localStorage.setItem('theme', sombre ? 'dark' : 'light');
    } catch (e) { /* navigation privée : préférence non persistée */ }
    var bouton = document.getElementById('basculer_theme');
    if (bouton) {
        bouton.textContent = sombre ? '☀️' : '🌙';
        bouton.title = sombre ? 'Passer en mode jour' : 'Passer en mode nuit';
    }
}

/* Met l'icône du bouton en accord avec le thème au chargement de chaque page */
document.addEventListener('DOMContentLoaded', function () {
    var bouton = document.getElementById('basculer_theme');
    if (bouton) {
        var sombre = document.documentElement.classList.contains('dark');
        bouton.textContent = sombre ? '☀️' : '🌙';
        bouton.title = sombre ? 'Passer en mode jour' : 'Passer en mode nuit';
    }
});

/* Navbar : ombre portée dès que la page est défilée */
window.addEventListener('scroll', function () {
    var nav = document.querySelector('nav');
    if (nav) nav.classList.toggle('ombre-defilement', window.scrollY > 8);
}, { passive: true });
