import React, {useState} from 'react';
import {ToolTip} from 'ui/components/ToolTip';

function SideNav() {
    const [isNavExpanded, setIsNavExpanded] = useState(false);
    const handleNavExpanded = event => {
        setIsNavExpanded(current => !current);
    }

    return (
        <nav className={`nav-block ${isNavExpanded ? 'nav-block--pinned' : ''}`}>
            <h3 className="a11y-only">Side Navigation</h3>
            <ul className="sidenav">
                <li className='d-phone-none'>
                    <ToolTip placement="left" title={isNavExpanded ? "Collapse" : "Expand"}>
                        <button className='nav-block__pin-button' aria-label={isNavExpanded ? "Collapse" : "Expand"} onClick={handleNavExpanded}>
                            <i className="icon--arrow-end" role='presentation'></i>
                        </button>
                    </ToolTip>
                </li>          
                <li className="sidenav__item">
                    <a href="/" title="" data-toggle="tooltip" data-placement="right" aria-label="Home" role="button" data-original-title="Home">
                        <span class="sidenav__item-icon">
                            <i className="icon--home" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Home</span>
                    </a>
                </li>
                <li className="sidenav__item active">
                    <a href="/wire" title="" data-toggle="tooltip" data-placement="right" aria-label="Wire" role="button" data-original-title="Wire">
                        <span id="saved-items-count" className="sidenav__badge">80</span>
                        <span class="sidenav__item-icon">
                            <i className="icon--text" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Wire</span>
                    </a>
                </li>
                <li className="sidenav__item">
                    <a href="/agenda" title="" data-toggle="tooltip" data-placement="right" aria-label="Agenda" role="button" data-original-title="Agenda">
                        <span class="sidenav__item-icon">
                            <i className="icon--calendar" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Agenda</span>
                    </a>
                </li>
                <li className="sidenav__item">
                    <a href="/monitoring" title="" data-toggle="tooltip" data-placement="right" aria-label="Monitoring" role="button" data-original-title="Monitoring">
                        <span class="sidenav__item-icon">
                            <i className="icon--monitoring" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Monitoring</span>
                    </a>
                </li>

                <li className="sidenav__separator" role='presentation'>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                </li>

                <li className="sidenav__item">
                    <a href="/bookmarks_wire" title="" data-toggle="tooltip" data-placement="right" aria-label="Saved / Watched Items" role="button" data-original-title="Saved / Watched">
                        <span id="saved-items-count" className="sidenav__badge">89</span>
                        <span class="sidenav__item-icon">
                           <i className="icon--bookmark" role='presentation'></i> 
                        </span>
                        <span className="sidenav__item-title">Saved / Watched</span>
                    </a>
                </li>

                <li className="sidenav__separator" role='presentation'>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                    <span className="separator__dot" aria-hidden="true"></span>
                </li>

                <li className="sidenav__item">
                    <a href="https://www.cpimages.com/" title="" data-toggle="tooltip" data-placement="right" aria-label="CP Images" target="_blank" data-original-title="CP Images">      
                        <span class="sidenav__item-icon">
                            <span className="sidenav__helper-icon">
                                <i className="icon-small--external" role='presentation'></i>
                            </span>
                            <i className="icon--photo"></i>
                        </span>
                        <span className="sidenav__item-title">CP Images</span>
                    </a>                    
                </li>

                <li className="sidenav__stretch-separator" role='presentation'></li>

                <li className="sidenav__item">
                    <a href="/reports/company_reports" title="" aria-label="Reports" role="button" data-toggle="tooltip" data-placement="right" data-original-title="Reports">
                        <span className="sidenav__item-icon">
                            <i className="icon--report" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Reports</span>
                    </a>
                </li>            
                <li className="sidenav__item">
                    <a href="/settings/companies" title="" aria-label="Settings" role="button" data-toggle="tooltip" data-placement="right" data-original-title="Settings">
                        <span className="sidenav__item-icon">
                            <i className="icon--cog" role='presentation'></i>
                        </span>
                        <span className="sidenav__item-title">Settings</span>
                    </a>
                </li>  
            </ul>
        </nav>
    )
}

export default SideNav;