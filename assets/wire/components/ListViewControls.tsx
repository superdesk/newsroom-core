import React from 'react';
import PropTypes from 'prop-types';

import {noNavigationSelected} from 'search/utils';

import NewsOnlyControl from './NewsOnlyControl';
import SearchAllVersionsControl from './SearchAllVersionsControl';
import ListViewOptions from '../../components/ListViewOptions';
import {ListSearchOptions} from './ListSearchOptions';
import NewItemsIcon from 'search/components/NewItemsIcon';
import {isMobilePhoneScreen} from 'utils';
import {ResizeObserverComponent} from '@superdesk/common';

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
    newItems,
    fetchItems,
}: any) {
    const Wrapper = ({children}: any) => {
        if (children == null) {
            return null;
        }
        return (
            <div className="navbar navbar--flex navbar--small navbar--list-controls">
                {children}
            </div>
        );
    };

    const renderRefreshButton = () => {
        return (newItems || []).length
            ? (
                <div className="navbar__inner navbar__inner--icon">
                    <NewItemsIcon
                        newItems={newItems}
                        refresh={fetchItems}
                    />
                </div>
            )
            : null;
    };

    return (
        <ResizeObserverComponent>
            {(dimensions) => (
                isMobilePhoneScreen(dimensions.width)
                    ? (
                        <Wrapper>{renderRefreshButton()}</Wrapper>
                    )
                    : (
                        <Wrapper>
                            {renderRefreshButton()}
                            <div className="navbar__inner navbar__inner--end navbar__inner--buttons">
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
                        </Wrapper>
                    )
            )}
        </ResizeObserverComponent>
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
    newItems: PropTypes.array,
    fetchItems: PropTypes.func,
};

export default ListViewControls;
