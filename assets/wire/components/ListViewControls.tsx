import React from 'react';
import {noNavigationSelected} from 'search/utils';
import NewsOnlyControl from './NewsOnlyControl';
import SearchAllVersionsControl from './SearchAllVersionsControl';
import ListViewOptions from '../../components/ListViewOptions';
import {ListSearchOptions} from './ListSearchOptions';
import NewItemsIcon from 'search/components/NewItemsIcon';
import {isMobilePhoneScreen} from 'utils';
import {WithScreenSizeObserver} from '@sourcefabric/common';
import {IArticle} from 'interfaces';

interface IProps {
    activeView?: string;
    newsOnly?: boolean;
    activeNavigation?: Array<string>;
    hideNewsOnly?: boolean;
    hideSearchAllVersions?: boolean;
    searchAllVersions?: boolean;
    newItems?: Array<IArticle['_id']>;
    setView: (view: {type: string, label: string}) => void;
    toggleSearchAllVersions?: () => void;
    toggleNews?: () => void;
    fetchItems: () => void;
}

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
}: IProps) {
    const renderRefreshButton = (newItems || []).length > 0 && (
        <div className="navbar__inner navbar__inner--icon">
            <NewItemsIcon
                newItems={newItems}
                refresh={fetchItems}
            />
        </div>
    );

    return (
        <WithScreenSizeObserver>
            {(dimensions) => (
                <div className="navbar navbar--flex navbar--small navbar--list-controls">
                    {isMobilePhoneScreen(dimensions.width)
                        ? renderRefreshButton
                        : (
                            <>
                                {renderRefreshButton}
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
                            </>
                        )
                    }
                </div>
            )}
        </WithScreenSizeObserver>
    );
}

export default ListViewControls;
