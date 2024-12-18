import React from 'react';
import AgendaFeaturedStoriesToogle from './AgendaFeaturedStoriesToogle';
import {DISPLAY_AGENDA_FEATURED_STORIES_ONLY, isMobilePhoneScreen} from 'utils';
import ListViewOptions from 'components/ListViewOptions';
import NewItemsIcon from 'search/components/NewItemsIcon';
import {WithScreenSizeObserver} from '@sourcefabric/common';
import {IAgendaItem, IEvent} from 'interfaces';

interface IProps {
    activeView?: string;
    hideFeaturedToggle?: boolean;
    featuredFilter?: boolean;
    hasAgendaFeaturedItems?: boolean;
    newItems?: Array<IAgendaItem['_id']>;
    setView: (view: {type: string, label: string}) => void;
    toggleFeaturedFilter: (event: IEvent) => void;
    fetchItems: () => void;
}

function AgendaListViewControls({activeView, setView, hideFeaturedToggle, toggleFeaturedFilter, featuredFilter, hasAgendaFeaturedItems, newItems, fetchItems}: IProps) {
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
                                    {!hideFeaturedToggle && hasAgendaFeaturedItems  && DISPLAY_AGENDA_FEATURED_STORIES_ONLY &&
                                        <AgendaFeaturedStoriesToogle onChange={toggleFeaturedFilter} featuredFilter={featuredFilter}/>
                                    }
                                    <ListViewOptions setView={setView} activeView={activeView} />
                                </div>
                            </>
                        )
                    }
                </div>
            )}
        </WithScreenSizeObserver>
    );
}

export default AgendaListViewControls;
