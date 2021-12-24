import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext, isWireContext} from 'utils';

import {removeNewItems} from 'wire/actions';
import FilterButton from 'wire/components/filters/FilterButton';
import {loadMyWireTopic} from 'wire/actions';
import {loadMyAgendaTopic} from 'agenda/actions';
import {CollapseBoxWithButton} from '../../ui/components/Collapse';
import {TopicItem} from './TopicItem';
import {globalTopicsEnabledSelector} from 'ui/selectors';

const tabName = isWireContext() ? 'Wire Topics' : 'Agenda Topics';
const manageTopics = () => document.dispatchEvent(window.manageTopics);

function TopicsTab({topics, loadMyTopic, newItemsByTopic, activeTopic, removeNewItems, globalTopicsEnabled}) {
    const clickTopic = (event, topic) => {
        event.preventDefault();
        removeNewItems(topic._id);
        loadMyTopic(topic);
    };

    const clickManage = (event) => {
        event.preventDefault();
        manageTopics();
    };

    const topicClass = (topic) => (
        `btn btn-block btn-outline-${topic._id === activeTopicId ? 'primary' : 'secondary'}`
    );

    const activeTopicId = activeTopic ? activeTopic._id : null;
    const personalTopics = (topics || []).filter(
        (topic) => !topic.is_global
    );
    const globalTopics = (topics || []).filter(
        (topic) => topic.is_global
    );

    return !globalTopicsEnabled ? (
        <React.Fragment>
            {!personalTopics.length ? (
                <div className='wire-column__info m-3'>
                    {gettext('No {{name}} created.', {name: tabName})}
                </div>
            ) : (
                <div className="m-3">
                    {personalTopics.map((topic) => (
                        <TopicItem
                            key={topic._id}
                            topic={topic}
                            newItemsByTopic={newItemsByTopic}
                            onClick={clickTopic}
                            className={topicClass(topic)}
                        />
                    ))}
                </div>
            )}
            <FilterButton
                label={gettext('Manage my {{name}}', {name: tabName})}
                onClick={clickManage}
                className='reset filter-button--border'
                primary={true}
            />
        </React.Fragment>
    ) : (
        <React.Fragment>
            <CollapseBoxWithButton
                id="my-topics"
                buttonText={gettext('My Topics')}
                initiallyOpen={true}
            >
                {!personalTopics.length ? (
                    <div className='wire-column__info m-3'>
                        {gettext('No {{name}} created.', {name: tabName})}
                    </div>
                ) : (
                    <div className="m-3">
                        {personalTopics.map((topic) => (
                            <TopicItem
                                key={topic._id}
                                topic={topic}
                                newItemsByTopic={newItemsByTopic}
                                onClick={clickTopic}
                                className={topicClass(topic)}
                            />
                        ))}
                    </div>
                )}
            </CollapseBoxWithButton>
            <CollapseBoxWithButton
                id="company-topics"
                buttonText={gettext('Company Topics')}
                initiallyOpen={true}
            >
                {!globalTopics.length ? (
                    <div className='wire-column__info m-3'>
                        {gettext('No {{name}} created.', {name: tabName})}
                    </div>
                ) : (
                    <div className="m-3">
                        {globalTopics.map((topic) => (
                            <TopicItem
                                key={topic._id}
                                topic={topic}
                                newItemsByTopic={newItemsByTopic}
                                onClick={clickTopic}
                                className={topicClass(topic)}
                            />
                        ))}
                    </div>
                )}
            </CollapseBoxWithButton>
            <FilterButton
                label={gettext('Manage my {{name}}', {name: tabName})}
                onClick={clickManage}
                className='reset filter-button--border'
                primary={true}
            />
        </React.Fragment>
    );
}

TopicsTab.propTypes = {
    topics: PropTypes.array.isRequired,
    newItemsByTopic: PropTypes.object,
    activeTopic: PropTypes.object,

    removeNewItems: PropTypes.func.isRequired,
    loadMyTopic: PropTypes.func.isRequired,
    globalTopicsEnabled: PropTypes.object,
};

const mapStateToProps = (state) => ({
    topics: state.topics || [],
    newItemsByTopic: state.newItemsByTopic,
    globalTopicsEnabled: globalTopicsEnabledSelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    removeNewItems: (topicId) => dispatch(removeNewItems(topicId)),
    loadMyTopic: (topic) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
});

export default connect(mapStateToProps, mapDispatchToProps)(TopicsTab);
