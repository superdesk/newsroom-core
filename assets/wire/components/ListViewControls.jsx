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
        <div className="navbar navbar--flex navbar--small">
            <div className="navbar__inner navbar__inner--end">
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
                <span className="navbar__divider"></span>
                <ListViewOptions setView={setView} activeView={activeView} />
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
            </div>
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
    hideSearchAllVersions: PropTypes.bool,
    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
};

export default ListViewControls;
