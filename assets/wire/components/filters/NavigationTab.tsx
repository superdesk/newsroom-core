import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'assets/utils';
import NavLink from './NavLink';
import {noNavigationSelected} from 'assets/search/utils';
import {toggleNavigation} from 'assets/search/actions';

function NavigationTab({
    navigations,
    activeNavigation,
    toggleNavigation,
    fetchItems,
    addAllOption,
    disableSameNavigationDeselect,
}: any) {
    const navLinks = navigations.map((navigation: any) => (
        <NavLink key={navigation.name}
            isActive={activeNavigation.includes(navigation._id) || navigations.length === 1}
            onClick={(event) => {
                event.preventDefault();
                toggleNavigation(navigation, disableSameNavigationDeselect);
                fetchItems();
            }}
            label={navigation.name}
        />
    ));

    const all = (
        <NavLink key="all"
            isActive={noNavigationSelected(activeNavigation)}
            onClick={(event) => {
                event.preventDefault();
                toggleNavigation();
                fetchItems();
            }}
            label={gettext('All')}
        />
    );

    return (
        <div className="m-3">
            {navLinks.length > 1 && addAllOption ? [all].concat(navLinks) : navLinks}
        </div>
    );
}

NavigationTab.propTypes = {
    navigations: PropTypes.arrayOf(PropTypes.object),
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
    toggleNavigation: PropTypes.func.isRequired,
    fetchItems: PropTypes.func.isRequired,
    addAllOption: PropTypes.bool,
    disableSameNavigationDeselect: PropTypes.bool,
};

NavigationTab.defaultProps = {addAllOption: true};

const mapDispatchToProps = {
    toggleNavigation,
};

export default connect(null, mapDispatchToProps)(NavigationTab);
