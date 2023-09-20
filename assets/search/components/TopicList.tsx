import React from 'react';
import {get} from 'lodash';
import {Topic} from './Topic';
import {Vertical} from 'sortable-containers/MultipleContainers';
import {TopicFolder} from './TopicFolder';
import {TopicNoDrag} from './TopicNoDrag';

export interface ITopic {
    _id: string;
    query: string;
    topic_type: string;
    label: string;
    timezone_offset: number;
    user: string;
    company?: string;
    is_global?: boolean;
    original_creator: string;
    version_creator: string;
    _created: string;
    _updated: string;
    _etag: string;
    folder?: string;
    name?: string;
    description?: string;
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
    createNewFolder,
}: any): any => {
    if (get(topics, 'length', 0) < 0 && get(folders, 'length', 0) < 0) {
        return null;
    }

    const renderTopic = (topic: any) => (
        <TopicNoDrag key={topic._id} topic={topic} actions={actions} users={users} selected={selectedTopicId === topic._id} />
    );

    const topicsByFolder = [...folders, {_id: 'no-folder'}].map((folder: any) => {
        return {
            folderId: folder?._id,
            itemsByFolder: topics?.map((f) => ({...f, folder: 'no-folder'})).filter((topic: any) => topic?.folder === folder?._id) ?? [{}]
        };
    });

    // pass folder ids separately to check wether this fixes the bug from useState
    return <Vertical folderIds={[...(folders.map((x) => x._id)), '64e896acb8f012cfed44c4bc']} createNewFolder={createNewFolder} items={topicsByFolder} renderItem={renderTopic} />;
    // const renderedFolders = folders.map((folder: any) => {
    //     const filteredTopics = topics.filter((topic: any) => topic.folder === folder._id);

    //     return (
    //         <TopicFolder
    //             key={folder._id}
    //             folder={folder}
    //             topics={filteredTopics}
    //             folderPopover={folderPopover}
    //             toggleFolderPopover={toggleFolderPopover}
    //             moveTopic={moveTopic}
    //             saveFolder={saveFolder}
    //             deleteFolder={deleteFolder}
    //         >
    //             {filteredTopics.map(renderTopic)}
    //         </TopicFolder>
    //     );
    // });

    // const renderedTopics = topics.filter((topic: any) => topic.folder == null).map(renderTopic);

    // return Array.prototype.concat(renderedFolders, renderedTopics);
};

export default TopicList;
