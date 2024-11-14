import React from 'react';
import PropTypes from 'prop-types';
import AgendaFeaturedStoriesToogle from './AgendaFeaturedStoriesToogle';
import {DISPLAY_AGENDA_FEATURED_STORIES_ONLY} from 'utils';
import ListViewOptions from 'components/ListViewOptions';
import NewItemsIcon from 'search/components/NewItemsIcon';

function AgendaListViewControls({activeView, setView, hideFeaturedToggle, toggleFeaturedFilter, featuredFilter, hasAgendaFeaturedItems, newItems, fetchItems}: any) {
    return (
        <div className="navbar navbar--flex navbar--small navbar--list-controls">
            {!(newItems || []).length ? null : (
                <div className="navbar__inner navbar__inner--icon">
                    <NewItemsIcon
                        newItems={newItems}
                        refresh={fetchItems}
                    />
                </div>
            )}
            <div className="navbar__inner navbar__inner--end navbar__inner--buttons">
                {!hideFeaturedToggle && hasAgendaFeaturedItems  && DISPLAY_AGENDA_FEATURED_STORIES_ONLY &&
                    <AgendaFeaturedStoriesToogle onChange={toggleFeaturedFilter} featuredFilter={featuredFilter}/>
                }
                <ListViewOptions setView={setView} activeView={activeView} />
            </div>
        </div>
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
