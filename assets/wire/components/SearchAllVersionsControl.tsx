import * as React from 'react';
import PropTypes from 'prop-types';
import Toggle from 'react-toggle';
import {gettext} from 'utils';
import {noNavigationSelected} from 'search/utils';

function SearchAllVersionsControl({searchAllVersions, toggleSearchAllVersions, activeNavigation}: any) {
    return !noNavigationSelected(activeNavigation) ? null : (
        <div className="d-flex align-items-center px-2 px-sm-3">
            <div className="d-flex align-items-center">
                <label htmlFor='all-versions' className="me-2 mb-0">{gettext('All Versions')}</label>
                <Toggle
                    id="all-versions"
                    defaultChecked={searchAllVersions}
                    className='toggle-background'
                    icons={false}
                    onChange={toggleSearchAllVersions}/>
            </div>
        </div>
    );
}

SearchAllVersionsControl.propTypes = {
    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
};

export default SearchAllVersionsControl;
