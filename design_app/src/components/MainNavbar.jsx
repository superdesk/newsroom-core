import React from 'react';
import DesignNav from './DesignNav';

function MainNavbar() {
    return (
        <nav className="main navbar">
            <h3 className="a11y-only">main nav bar</h3>
            <div className="navbar__logo">
                <a href="#">
                    <h1 className="a11y-only">Newshub</h1>
                    <img src="static/logo.svg" alt="newshub" aria-hidden="true" />
                </a>
            </div>
            <div className="navbar-brand">
                <nav>
                <span className="breadcrumb-item active">Home</span>
                </nav>
                 <DesignNav />
            </div>

            <div className="navbar__right navbar__right--login">
                <div className="navbar__date">Tuesday, 13/12/2022</div>
                <a className="nav-link" href="#">Login</a>
                <a className="nav-link"
                   href="#"
                   target="_blank">Contact Us</a>
            </div>

        </nav>
    )
}

export default MainNavbar;
