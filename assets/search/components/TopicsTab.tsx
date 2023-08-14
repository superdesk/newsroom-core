import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext, isWireContext} from 'utils';

import {removeNewItems} from 'wire/actions';
import {loadMyWireTopic} from 'wire/actions';
import {loadMyAgendaTopic} from 'agenda/actions';
import {CollapseBoxWithButton} from '../../ui/components/Collapse';
import {TopicItem} from './TopicItem';
import {SidebarFolder} from '../../components/SidebarFolder';

const manageTopics = () => document.dispatchEvent(new Event('manage_topics'));

function TopicsTab({topics, loadMyTopic, newItemsByTopic, activeTopic, removeNewItems, userFolders, companyFolders}: any) {
    const clickTopic = (event: any, topic: any) => {
        event.preventDefault();
        removeNewItems(topic._id);
        loadMyTopic(topic);
    };

    const clickManage = (event: any) => {
        event.preventDefault();
        manageTopics();
    };

    const activeTopicId = activeTopic ? activeTopic._id : null;
    const personalTopics = (topics || []).filter(
        (topic: any) => !topic.is_global
    );
    const globalTopics = (topics || []).filter(
        (topic: any) => topic.is_global
    );

    const tabName = gettext('{{ section }} Topics', {section: isWireContext() ? window.sectionNames.wire : window.sectionNames.agenda});

    const renderTopic = (topic: any) => (
        <TopicItem key={topic._id}
            topic={topic}
            isActive={topic._id === activeTopicId}
            newItems={newItemsByTopic && newItemsByTopic[topic._id] ? newItemsByTopic[topic._id].length : 0}
            onClick={clickTopic}
        />
    );

    const renderTopicsSection = (folders: any, topics: any) => {
        if (topics.length === 0) {
            return (
                <div className='wire-column__info mb-4'>
                    {gettext('No {{name}} created.', {name: tabName})}
                </div>
            );
        }

        return (
            <React.Fragment>
                {renderFolders(folders, topics)}
                {renderFreeTopics(topics)}
            </React.Fragment>
        );

    };

    const renderFolders = (folders: any, topics: any) => folders.map((folder: any) => {
        const folderTopics = topics.filter((topic: any) => topic.folder === folder._id);

        if (folderTopics.length === 0) {
            return null;
        }

        return (
            <SidebarFolder key={folder._id} folder={folder}>
                {folderTopics.map(renderTopic)}
            </SidebarFolder>
        );
    });

    const renderFreeTopics = (topics: any) => {
        const filtered = topics.filter((topic: any) => !topic.folder);

        if (filtered.length === 0) {
            return null;
        }

        return (
            <ul className="topic-list topic-list--unsorted">
                {filtered.map(renderTopic)}
            </ul>
        );
    };

    return (
        <div className="tab-pane__inner">
            <div className="tab-content">
                <CollapseBoxWithButton
                    id="my-topics"
                    buttonText={gettext('My Topics')}
                    initiallyOpen={true}
                    edit={clickManage}
                >
                    {renderTopicsSection(userFolders, personalTopics)}
                </CollapseBoxWithButton>
                <CollapseBoxWithButton
                    id="company-topics"
                    buttonText={gettext('Company Topics')}
                    initiallyOpen={true}
                >
                    {renderTopicsSection(companyFolders, globalTopics)}
                </CollapseBoxWithButton>
            </div>
        </div>
    );
}

TopicsTab.propTypes = {
    topics: PropTypes.array.isRequired,
    newItemsByTopic: PropTypes.object,
    activeTopic: PropTypes.object,
    userFolders: PropTypes.array,
    companyFolders: PropTypes.array,

    removeNewItems: PropTypes.func.isRequired,
    loadMyTopic: PropTypes.func.isRequired,
};

const mapStateToProps = (state: any) => ({
    topics: state.topics || [],
    userFolders: state.userFolders || [],
    companyFolders: state.companyFolders || [],
    newItemsByTopic: state.newItemsByTopic,
});

const mapDispatchToProps = (dispatch: any) => ({
    removeNewItems: (topicId: any) => dispatch(removeNewItems(topicId)),
    loadMyTopic: (topic: any) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(TopicsTab);

export default component;
