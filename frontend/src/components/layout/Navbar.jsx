import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <NavLink to="/market" className="brand-logo-link" aria-label="Accueil Estate AI">
          <img className="brand-logo" src="/navbar-logo.png" alt="Plateforme Intelligente - Prediction et Analyse Immobiliere" />
        </NavLink>
        <nav className="topbar-nav">
          <NavLink to="/market">Marche</NavLink>
          <NavLink to="/prediction">Prediction</NavLink>
          <NavLink to="/assistant">Assistant IA</NavLink>
        </nav>
      </div>
    </header>
  );
}
