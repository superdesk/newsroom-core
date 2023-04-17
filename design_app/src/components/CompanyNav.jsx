import React from 'react';

function CompanyNav() {
    return (
        <div className="side-navigation" id="settings-menu">
            <h3 className="a11y-only">Settings Menu</h3>
            <ul>
                <li>
                    <a className="side-navigation__btn active" href="#">
                        Company User Management</a>
                </li>                        
            </ul>
        </div>
    )
}

export default CompanyNav;