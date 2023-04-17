import React from 'react';
import { NavLink } from 'react-router-dom';

function DesignNav() { 
    const items = [
        { path: '/', title: 'Home' },
        { path: '/wire', title: 'Wire' },
        //{ path: '/settings', title: 'Settings' },
        { path: '/company', title: 'Company' },
    ];
    
    return (        
        <nav className="navbar design navbar-expand-lg ms-5">
                <h6>Design Navigation:</h6>
                <ul className="navbar-nav">
                    {
                    items.map((item, i) => (
                        <li key={i} className="nav-item">
                        <NavLink className="nav-link" to={item.path}>{item.title}</NavLink>
                        </li>
                    ))
                    }
                </ul>
          
        </nav>
        
    );
}

export default DesignNav;