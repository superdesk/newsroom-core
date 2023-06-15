import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import {canUserUpdateTopic} from 'users/utils';
import {SearchResultTagList} from './SearchResultTagList';

export function SearchResultsTopicRow({
    user,
    searchParams,
    activeTopic,
    navigations,
    showSaveTopic,
    topicType,
    saveMyTopic,
    toggleNavigation,
    refresh,
    deselectMyTopic,
}) {
    const tags = [];
    const buttons = [];
    const hasActiveTopic = get(activeTopic, '_id') != null;

    if (hasActiveTopic) {
        tags.push({
            text: activeTopic.label,
            shade: 'inverse',
            onClick: () => {
                deselectMyTopic(activeTopic._id);
            },
        });

        if (showSaveTopic && canUserUpdateTopic(user, activeTopic)) {
            buttons.push((
                <button
                    key="update_topic_button"
                    className="btn btn-outline-secondary btn-responsive btn--small"
                    onClick={() => {
                        saveMyTopic(Object.assign(
                            {},
                            activeTopic,
                            searchParams,
                            {query: searchParams.query},
                            {topic_type: topicType},
                            {filter: searchParams.filter}
                        ));
                    }}
                >
                    {gettext('Update topic')}
                </button>
            ));
        }
    }

    if (get(searchParams, 'navigation.length', 0)) {
        searchParams.navigation.forEach((navId) => {
            const navigation = navigations[navId];

            tags.push({
                text: navigation.name,
                shade: 'inverse',
                onClick: () => {
                    toggleNavigation(navigation);
                    refresh();
                },
            });
        });
    }

    if (showSaveTopic) {
        buttons.push((
            <button
                key="save_topic_button"
                className="btn btn-outline-secondary btn-responsive btn--small"
                onClick={() => {
                    saveMyTopic(Object.assign(
                        {},
                        searchParams,
                        {topic_type: topicType},
                        {filter: searchParams.filter}
                    ));
                }}
            >
                {hasActiveTopic ? gettext('Save as new topic') : gettext('Save new topic')}
            </button>
        ));
    }

    if (!tags.length && !buttons.length) {
        return null;
    }

    return (
        <SearchResultTagList
            title={tags.length ? gettext('Topic') : null}
            tags={tags}
            buttons={buttons}
        />
    );
}

SearchResultsTopicRow.propTypes = {
    user: PropTypes.object,
    searchParams: PropTypes.object,
    activeTopic: PropTypes.object,
    navigations: PropTypes.object,
    showSaveTopic: PropTypes.bool,
    topicType: PropTypes.string,
    saveMyTopic: PropTypes.func,
    toggleNavigation: PropTypes.func.isRequired,
    refresh: PropTypes.func.isRequired,
    deselectMyTopic: PropTypes.func.isRequired,
};
