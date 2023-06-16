import React from 'react';
import PropTypes from 'prop-types';

import {get} from 'lodash';

import {Topic} from './Topic';
import {TopicFolder} from './TopicFolder';

const TopicList = ({topics, selectedTopicId, actions, users, folders, folderPopover, toggleFolderPopover, moveTopic, saveFolder, deleteFolder}) => {

    if (get(topics, 'length', 0) < 0 && get(folders, 'length', 0) < 0) {
        return null;
    }

    const renderTopic = (topic) => (
        <Topic key={topic._id} topic={topic} actions={actions} users={users} selected={selectedTopicId === topic._id} />
    );

    const renderedFolders = folders.map((folder) => {
        const filteredTopics = topics.filter((topic) => topic.folder === folder._id);
        return (
            <TopicFolder key={folder._id}
                folder={folder}
                topics={filteredTopics}
                folderPopover={folderPopover}
                toggleFolderPopover={toggleFolderPopover}
                moveTopic={moveTopic}
                saveFolder={saveFolder}
                deleteFolder={deleteFolder}
            >
                {filteredTopics.map(renderTopic)}
            </TopicFolder>
        );
    });

    const renderedTopics = topics.filter((topic) => topic.folder == null).map(renderTopic);

    return Array.prototype.concat(renderedFolders, renderedTopics);
};

TopicList.propTypes = {
    topics: PropTypes.arrayOf(PropTypes.object),
    selectedTopicId: PropTypes.string,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        icon: PropTypes.string,
        action: PropTypes.func,
    })),
    users: PropTypes.array,
    folders: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
    })),
    folderPopover: PropTypes.string,
    toggleFolderPopover: PropTypes.func,
    moveTopic: PropTypes.func,
    saveFolder: PropTypes.func,
    deleteFolder: PropTypes.func,
};

export default TopicList;
