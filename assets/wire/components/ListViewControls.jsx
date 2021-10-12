import React from 'react';
import PropTypes from 'prop-types';

import NewsOnlyControl from './NewsOnlyControl';
import SearchAllVersionsControl from './SearchAllVersionsControl';
import ListViewOptions from '../../components/ListViewOptions';

function ListViewControls({
    activeView,
    setView,
    newsOnly,
    toggleNews,
    activeNavigation,
    hideNewsOnly,
    hideSearchAllVersions,
    searchAllVersions,
    toggleSearchAllVersions,
}) {
    return(
        <div className='content-bar__right'>
            {hideSearchAllVersions ? null : (
                <SearchAllVersionsControl
                    activeNavigation={activeNavigation}
                    searchAllVersions={searchAllVersions}
                    toggleSearchAllVersions={toggleSearchAllVersions}
                />
            )}
            {!hideNewsOnly && <NewsOnlyControl
                activeNavigation={activeNavigation}
                newsOnly={newsOnly}
                toggleNews={toggleNews}
            />}
            <ListViewOptions setView={setView} activeView={activeView} />
        </div>
    );
}


ListViewControls.propTypes = {
    activeView: PropTypes.string,
    setView: PropTypes.func.isRequired,
    newsOnly: PropTypes.bool,
    toggleNews: PropTypes.func,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
    hideNewsOnly: PropTypes.bool,

    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
};

export default ListViewControls;
