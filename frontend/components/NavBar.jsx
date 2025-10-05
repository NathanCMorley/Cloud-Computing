import React from "react";
import "../styles/NavBar.css";
import { Link } from "react-router-dom";

function NavBar() {
  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">JANDO</Link>
      </div>
      <div className="nav-links">
        <Link to="/home">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/map">Map</Link>
      </div>
    </nav>
  );
}

export default NavBar;
