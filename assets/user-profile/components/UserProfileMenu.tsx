import React from 'react';
import PropTypes from 'prop-types';

function UserProfileMenu({links, onClick}: any) {
    return (
        <div className="profile-side-navigation__items">
            {links.map((link: any) => (
                <a key={link.name}
                    href="#"
                    className={`btn w-100 btn-outline-${link.active ? 'primary' : 'secondary'}`}
                    title={link.name}
                    onClick={(event: any) => onClick(event, link.name)}
                >{link.label}</a>
            ))}
        </div>
    );
}

UserProfileMenu.propTypes = {
    links: PropTypes.array,
    onClick: PropTypes.func,
};

export default UserProfileMenu;
