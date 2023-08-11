import React from 'react';
import DesignNav from './DesignNav';

function MainNavbar() {
    return (
        <nav className="main navbar">
            <h3 className="a11y-only">main nav bar</h3>
            <div className="navbar__logo">
                {/* Default */}
                <a href="#">
                    <h1 className="a11y-only">Newsroom</h1>
                    <img className="navbar__logo-img navbar__logo-img--en" src="static/logo.svg" alt="Newsroom" aria-hidden="true" />
                </a>
                
                {/* Canadian Press */}
                {/* <a href="#">
                    <h1 className="a11y-only">The Canadian Press</h1>
                    <img className="navbar__logo-img navbar__logo-img--en" src="static/temp_logos/logo.svg" alt="The Canadian Press" aria-hidden="true" />
                </a> */}

                {/* Canadian Press - French */}
                {/* <a href="#">
                    <h1 className="a11y-only">La Presse Canadienne</h1>
                    <img className="navbar__logo-img navbar__logo-img--fr" src="static/temp_logos/logo-fr.svg" alt="La Presse Canadienne" aria-hidden="true" />
                </a> */}
            </div>

            {/* NewsPro */}
            {/* <div className="navbar__additional-logo">
                <h1 className="a11y-only">NewsPro</h1>
                <img className="navbar__additional-logo-img navbar__additional-logo-img--en" src="static/temp_logos/logo-newspro.svg" alt="Newspro" aria-hidden="true" />
            </div> */}

            {/* NewsPro French */}
            {/* <div className="navbar__additional-logo">
                <h1 className="a11y-only">NouvellesPro</h1>
                <img className="navbar__additional-logo-img navbar__additional-logo-img--fr" src="static/temp_logos/logo-newspro-fr.svg" alt="NouvellesPro" aria-hidden="true" />
            </div> */}
            <div className="navbar-brand">
                <nav>
                    <span className="breadcrumb-item active">Home</span>
                </nav>
                 <DesignNav />
            </div>

            {/* <div className="navbar__right navbar__right--login">
                <div className="navbar__date">Tuesday, 05.07.2023</div>
                <a className="nav-link" href="#">Login</a>
                <a className="nav-link"
                   href="#"
                   target="_blank">Contact Us</a>
            </div> */}

            <div className="navbar__right">
                <div className="navbar__date">July 5, 2023, 12:02:33 PM EDT</div>
                <div className="navbar-notifications navbar-notifications--open" id="header-notification">

                    <div className="navbar-notifications__inner">
                        <h3 className="a11y-only">Notification Bell</h3>
                        <div className="navbar-notifications__badge">379</div>
                        <span className="navbar-notifications__inner-circle" title="" data-bs-original-title="Notifications">
                            <h3 className="a11y-only">Notification bell</h3>
                            <i className="icon--alert"></i>
                        </span>

                        <div className="notif__list dropdown-menu dropdown-menu-right show--">
                            <div className="notif__list__header d-flex">
                                <span className="notif__list__header-headline ms-3">Notifications</span>
                                <button type="button" className="button-pill ms-auto me-3">Clear All</button>
                            </div>
                            {/* Item 1 */}
                            <div className="notif__list__item">
                                <button type="button" className="close" aria-label="Close" role="button">
                                    <span aria-hidden="true">×</span>
                                </button>
                                <div className="notif__list__info">A story has arrived that matches a subscribed topic</div>
                                <div className="notif__list__headline">
                                    <a href="/wire?item=b8ad40d5-cd15-4266-a684-93cec30aed2c">AP News Digest 2 pm</a>
                                </div>
                                <div className="wire-articles__item__meta-info">Created at 19:56</div>
                            </div>
                            {/* Item 2 */}
                            <div className="notif__list__item">
                                <button type="button" className="close" aria-label="Close" role="button">
                                    <span aria-hidden="true">×</span>
                                </button>
                                <div className="notif__list__info">A story has arrived that matches a subscribed topic</div>
                                <div className="notif__list__headline">
                                    <a href="/wire?item=b8ad40d5-cd15-4266-a684-93cec30aed2c">Dutch museums will return art and artifacts that were looted from Sri Lanka and Indonesia</a>
                                </div>
                                <div className="wire-articles__item__meta-info">Created on Jul 6th, 2023</div>
                            </div>
                        </div>

                    </div>
                </div>
                <div id="header-profile-toggle">
                    <div className="header-profile">
                        <figure className="header-profile__avatar">
                            <span className="header-profile__characters" title="" data-bs-original-title="Admin Admin">AA</span>
                        </figure>
                    </div>
                    {/* <div className="dropdown-menu dropdown-menu-right show"><div className="card card--inside-dropdown"><div className="card-header">Admin Admin</div><ul className="list-group list-group-flush"><li className="list-group-item list-group-item--link"><a href="">My Profile<i className="svg-icon--arrow-right"></i></a></li><li className="list-group-item list-group-item--link"><a href="">My Wire Topics<i className="svg-icon--arrow-right"></i></a></li><li className="list-group-item list-group-item--link"><a href="">My Agenda Topics<i className="svg-icon--arrow-right"></i></a></li><li className="list-group-item list-group-item--link"><a href="">My Monitoring<i className="svg-icon--arrow-right"></i></a></li></ul><div className="card-footer"><a href="/logout" className="nh-button nh-button--tertiary float-end">Logout</a></div></div></div> */}
                </div>
            </div>

        </nav>
    )
}

export default MainNavbar;
