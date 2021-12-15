import React from 'react';
import PropTypes from 'prop-types';

import {noNavigationSelected} from 'search/utils';

import NewsOnlyControl from './NewsOnlyControl';
import SearchAllVersionsControl from './SearchAllVersionsControl';
import ListViewOptions from '../../components/ListViewOptions';
import {ListSearchOptions} from './ListSearchOptions';

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
        <React.Fragment>
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
            {(!noNavigationSelected(activeNavigation) || (hideSearchAllVersions && hideNewsOnly)) ? null : (
                <div className="content-bar__right--mobile">
                    <ListSearchOptions
                        hideSearchAllVersions={hideSearchAllVersions}
                        searchAllVersions={searchAllVersions}
                        toggleSearchAllVersions={toggleSearchAllVersions}
                        hideNewsOnly={hideNewsOnly}
                        newsOnly={newsOnly}
                        toggleNews={toggleNews}
                    />
                </div>
            )}
        </React.Fragment>
    );
}


ListViewControls.propTypes = {
    activeView: PropTypes.string,
    setView: PropTypes.func.isRequired,
    newsOnly: PropTypes.bool,
    toggleNews: PropTypes.func,
    activeNavigation: PropTypes.arrayOf(PropTypes.string),
    hideNewsOnly: PropTypes.bool,
    hideSearchAllVersions: PropTypes.bool,
    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
};

export default ListViewControls;
