import React from 'react';
import PropTypes from 'prop-types';
import AgendaFeaturedStoriesToogle from './AgendaFeaturedStoriesToogle';
import {DISPLAY_AGENDA_FEATURED_STORIES_ONLY, isMobilePhoneScreen} from 'utils';
import ListViewOptions from 'components/ListViewOptions';
import NewItemsIcon from 'search/components/NewItemsIcon';
import {ResizeObserverComponent} from '@superdesk/common';

function AgendaListViewControls({activeView, setView, hideFeaturedToggle, toggleFeaturedFilter, featuredFilter, hasAgendaFeaturedItems, newItems, fetchItems}: any) {
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
                                {!hideFeaturedToggle && hasAgendaFeaturedItems  && DISPLAY_AGENDA_FEATURED_STORIES_ONLY &&
                                    <AgendaFeaturedStoriesToogle onChange={toggleFeaturedFilter} featuredFilter={featuredFilter}/>
                                }
                                <ListViewOptions setView={setView} activeView={activeView} />
                            </div>
                        </Wrapper>
                    )
            )}
        </ResizeObserverComponent>
    );
}


AgendaListViewControls.propTypes = {
    activeView: PropTypes.string,
    setView: PropTypes.func.isRequired,
    toggleFeaturedFilter: PropTypes.func.isRequired,
    hideFeaturedToggle: PropTypes.bool,
    featuredFilter: PropTypes.bool,
    hasAgendaFeaturedItems: PropTypes.bool,
    newItems: PropTypes.array,
    fetchItems: PropTypes.func,
};

export default AgendaListViewControls;
