import React from 'react';

function SideNav() {
    return (
    
        <nav className="sidenav">
            <h3 className="a11y-only">Side Navigation</h3>
            <ul className="sidenav-icons">           
                <li className="sidenav-icons__item">
                    <a href="/" title="" data-toggle="tooltip" data-placement="right" aria-label="Home" role="button" data-original-title="Home"><i className="icon--home"></i>
                    <div className="sidenav-icons__item-title">Home</div>
                    </a>
                </li>
                <li className="sidenav-icons__item active">
                    <a href="/wire" title="" data-toggle="tooltip" data-placement="right" aria-label="Wire" role="button" data-original-title="Wire"> <i className="icon--text"></i>
                    <div className="sidenav-icons__item-title">Wire</div>
                    </a>
                </li>
                <li className="sidenav-icons__item">
                    <a href="/agenda" title="" data-toggle="tooltip" data-placement="right" aria-label="Agenda" role="button" data-original-title="Agenda"><i className="icon--calendar"></i>
                    <div className="sidenav-icons__item-title">Agenda</div>
                    </a>
                </li>
                <li className="sidenav-icons__item">
                    <a href="/monitoring" title="" data-toggle="tooltip" data-placement="right" aria-label="Monitoring" role="button" data-original-title="Monitoring"><i className="icon--monitoring"></i>
                    <div className="sidenav-icons__item-title">Monitoring</div>
                    </a>
                </li>

                <li className="sidenav-icons__separator">
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                </li>

                <li className="sidenav-icons__item">
                    <a href="/bookmarks_wire" title="" data-toggle="tooltip" data-placement="right" aria-label="Saved / Watched Items" role="button" data-original-title="Saved / Watched">
                    <div id="saved-items-count" className="sidenav-icons__badge">2</div>
                    <i className="icon--bookmark"></i>
                    <div className="sidenav-icons__item-title">Saved / Watched</div>
                    </a>
                </li>

                <li className="sidenav-icons__separator">
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                </li>

                <li className="sidenav-icons__item">
                    <a href="https://www.cpimages.com/" title="" data-toggle="tooltip" data-placement="right" aria-label="CP Images" target="_blank" data-original-title="CP Images">      
                        <div className="sidenav-icons__helper-icon">
                            <i className="icon-small--external"></i>
                        </div>        
                        <i className="icon--photo"></i>
                        <div className="sidenav-icons__item-title">CP Images</div>
                    </a>                    
                </li>

                <li className="sidenav-icons__stretch-separator"></li>

                <li className="sidenav-icons__item">
                    <a href="/reports/company_reports" title="" aria-label="Reports" role="button" data-toggle="tooltip" data-placement="right" data-original-title="Reports">
                    <i className="icon--report"></i>
                    <div className="sidenav-icons__item-title">Reports</div>
                    </a>
                </li>            
                <li className="sidenav-icons__item">
                    <a href="/settings/companies" title="" aria-label="Settings" role="button" data-toggle="tooltip" data-placement="right" data-original-title="Settings">
                    <i className="icon--cog"></i>
                    <div className="sidenav-icons__item-title">Settings</div>
                    </a>
                </li>  
            </ul>
        </nav>
    )
}

export default SideNav;