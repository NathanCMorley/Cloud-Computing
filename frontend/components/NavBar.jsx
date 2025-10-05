import React from "react";
import { Link } from "react-router-dom";

function NavBar() {
  return (
    <nav className="nav">
      <div className="logo">
        <Link className="nav-link" to="/home">
          Educational
        </Link>
      </div>
      <div className="nav-item">
        <Link className="nav-link" to="/home">
          Technical
        </Link>
      </div>
    </nav>
  );
}

export default NavBar;
