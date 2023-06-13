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

const manageTopics = () => document.dispatchEvent(new Event('manage_topics'));

function TopicsTab({topics, loadMyTopic, newItemsByTopic, activeTopic, removeNewItems, globalTopicsEnabled}: any) {
    const clickTopic = (event: any, topic: any) => {
        event.preventDefault();
        removeNewItems(topic._id);
        loadMyTopic(topic);
    };

    const clickManage = (event: any) => {
        event.preventDefault();
        manageTopics();
    };

    const topicClass = (topic: any) => (
        `btn w-100 btn-outline-${topic._id === activeTopicId ? 'primary' : 'secondary'}`
    );

    const activeTopicId = activeTopic ? activeTopic._id : null;
    const personalTopics = (topics || []).filter(
        (topic: any) => !topic.is_global
    );
    const globalTopics = (topics || []).filter(
        (topic: any) => topic.is_global
    );

    const tabName = gettext('{{ section }} Topics', {section: isWireContext() ? window.sectionNames.wire : window.sectionNames.agenda});

    return !globalTopicsEnabled ? (
        <React.Fragment>
            {!personalTopics.length ? (
                <div className='wire-column__info mb-3'>
                    {gettext('No {{name}} created.', {name: tabName})}
                </div>
            ) : (
                <div className="my-3">
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
                className='filter-button--border'
                primary={true}
            />
        </React.Fragment>
    ) : (
        <React.Fragment>
            <div className='tab-pane__inner'>
                <CollapseBoxWithButton
                    id="my-topics"
                    buttonText={gettext('My Topics')}
                    initiallyOpen={true}
                >
                    {!personalTopics.length ? (
                        <div className='wire-column__info mb-4'>
                            {gettext('No {{name}} created.', {name: tabName})}
                        </div>
                    ) : (
                        <div className="mb-3">
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
                        <div className='wire-column__info mb-4'>
                            {gettext('No {{name}} created.', {name: tabName})}
                        </div>
                    ) : (
                        <div className="mb-3">
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
            </div>
            <FilterButton
                label={gettext('Manage my {{name}}', {name: tabName})}
                onClick={clickManage}
                className='filter-button--border'
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
    globalTopicsEnabled: PropTypes.bool,
};

const mapStateToProps = (state: any) => ({
    topics: state.topics || [],
    newItemsByTopic: state.newItemsByTopic,
    globalTopicsEnabled: globalTopicsEnabledSelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    removeNewItems: (topicId: any) => dispatch(removeNewItems(topicId)),
    loadMyTopic: (topic: any) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
});

export default connect(mapStateToProps, mapDispatchToProps)(TopicsTab);
