import React from 'react';
import PropTypes from 'prop-types';

import AgendaFeaturedStoriesToogle from './AgendaFeaturedStoriesToogle.jsx';
import {DISPLAY_AGENDA_FEATURED_STORIES_ONLY} from 'utils';
import ListViewOptions from 'components/ListViewOptions';

function AgendaListViewControls({activeView, setView, hideFeaturedToggle, toggleFeaturedFilter, featuredFilter, hasAgendaFeaturedItems}) {
    return (
        <div className="navbar navbar--flex navbar--small">
            <div className="navbar__inner navbar__inner--end">
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
};

export default AgendaListViewControls;
