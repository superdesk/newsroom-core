import React from 'react';

import {get} from 'lodash';

import {ITopicAction, Topic} from './Topic';
import {TopicFolder} from './TopicFolder';
import {ITopic, ITopicFolder, IUser} from 'interfaces';

interface IProps {
    topics: Array<ITopic>;
    selectedTopicId: ITopic['_id'];
    actions: Array<ITopicAction>;
    user: IUser;
    users: Array<IUser>;
    folders: Array<ITopicFolder>;
    folderPopover: string;
    toggleFolderPopover: (folder: ITopicFolder) => void;
    moveTopic: (topic: ITopic, folder: ITopicFolder) => Promise<any>;
    saveFolder: (folder: ITopicFolder, updates: Partial<ITopicFolder>) => Promise<any>;
    deleteFolder: (folder: ITopicFolder) => void;
}

const TopicList = ({
    topics,
    selectedTopicId,
    actions,
    user,
    users,
    folders,
    folderPopover,
    toggleFolderPopover,
    moveTopic,
    saveFolder,
    deleteFolder,
}: IProps) => {

    if (get(topics, 'length', 0) < 0 && get(folders, 'length', 0) < 0) {
        return null;
    }

    const renderTopic = (topic: ITopic) => {
        const subscription = topic.subscribers?.find((sub) => sub.user_id === user._id);
        return (
            <Topic key={topic._id}
                topic={topic}
                actions={actions}
                users={users}
                selected={selectedTopicId === topic._id}
                subscriptionType={subscription?.notification_type}
            />
        );
    };

    const renderedFolders = folders.map((folder) => {
        const filteredTopics = topics.filter((topic) => topic.folder === folder._id);
        return (
            <TopicFolder
                key={folder._id}
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

    const renderedTopics = topics.filter((topic: any) => topic.folder == null).map(renderTopic);

    return (
        <>
            {renderedFolders}
            {renderedTopics}
        </>
    );
};

export default TopicList;
