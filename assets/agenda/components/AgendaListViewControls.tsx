import React from 'react';
import PropTypes from 'prop-types';

import AgendaFeaturedStoriesToggle from './AgendaFeaturedStoriesToogle.jsx';
import {DISPLAY_AGENDA_FEATURED_STORIES_ONLY} from 'utils';
import ListViewOptions from 'components/ListViewOptions';

function AgendaListViewControls({activeView, setView, hideFeaturedToggle, toggleFeaturedFilter, featuredFilter, hasAgendaFeaturedItems}) {
    return(
        <div className='content-bar__right'>
            {!hideFeaturedToggle && hasAgendaFeaturedItems  && DISPLAY_AGENDA_FEATURED_STORIES_ONLY &&
                <AgendaFeaturedStoriesToggle onChange={toggleFeaturedFilter} featuredFilter={featuredFilter}/>
            }
            <ListViewOptions setView={setView} activeView={activeView} />
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
