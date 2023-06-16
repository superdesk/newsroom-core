import * as React from 'react';
import PropTypes from 'prop-types';
import Toggle from 'react-toggle';
import {gettext} from 'utils';
import {noNavigationSelected} from 'search/utils';

function SearchAllVersionsControl({searchAllVersions, toggleSearchAllVersions, activeNavigation}) {
    return !noNavigationSelected(activeNavigation) ? null : (
        <div className="react-toggle__wrapper">
            <label htmlFor='all-versions' className="me-2">{gettext('All Versions')}</label>
            <Toggle
                id="all-versions"
                defaultChecked={searchAllVersions}
                className='toggle-background'
                icons={false}
                onChange={toggleSearchAllVersions}/>
        </div>
    );
}

SearchAllVersionsControl.propTypes = {
    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
};

export default SearchAllVersionsControl;
