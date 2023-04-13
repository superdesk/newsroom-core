import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {loadMyAgendaTopic} from 'assets/agenda/actions';
import {CollapseBoxWithButton} from 'assets/ui/components/Collapse';
import {globalTopicsEnabledSelector} from 'assets/ui/selectors';
import {isWireContext, gettext} from 'assets/utils';
import {removeNewItems, loadMyWireTopic} from 'assets/wire/actions';
import FilterButton from 'assets/wire/components/filters/FilterButton';
import {TopicItem} from './TopicItem';

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

    const tabName = isWireContext() ? gettext('Wire Topics') : gettext('Agenda Topics');

    return !globalTopicsEnabled ? (
        <React.Fragment>
            {!personalTopics.length ? (
                <div className='wire-column__info m-3'>
                    {gettext('No {{name}} created.', {name: tabName})}
                </div>
            ) : (
                <div className="m-3">
                    {personalTopics.map((topic: any) => (
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
                        {personalTopics.map((topic: any) => (
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
                        {globalTopics.map((topic: any) => (
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
