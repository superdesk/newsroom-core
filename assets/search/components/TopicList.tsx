import React, {useState, createRef} from 'react';
import {get} from 'lodash';
import {DndContext, TraversalOrder} from '@dnd-kit/core';

import {ITopicAction, Topic} from './Topic';
import {TopicFolder} from './TopicFolder';
import {ITopic, ITopicFolder, IUser} from 'interfaces';

import {Draggable} from '../../components/drag-and-drop/draggable';
import {Overlay} from 'components/drag-and-drop/overlay';
import {useCustomSensors} from 'components/drag-and-drop/use-custom-sensors';
import {useScrollRestore} from 'components/drag-and-drop/use-scroll-restore';

interface IProps {
    topics: Array<ITopic>;
    selectedTopicId: ITopic['_id'];
    actions: Array<ITopicAction>;
    user: IUser;
    users: Array<IUser>;
    folders: Array<ITopicFolder>;
    folderPopover: string;
    toggleFolderPopover: (folder: ITopicFolder) => void;
    moveTopic: (topicId: ITopic['_id'], folder: ITopicFolder | null) => Promise<void>;
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

    const [openedFolders, setOpenedFolders] = useState<{[folderId: string]: boolean}>({});

    const renderTopic = (topic: ITopic) => {
        const subscription = topic.subscribers?.find((sub) => sub.user_id === user._id);

        return (
            <Draggable id={topic._id} key={topic._id} hideWhileDragging>
                <Topic
                    topic={topic}
                    actions={actions}
                    users={users}
                    selected={selectedTopicId === topic._id}
                    subscriptionType={subscription?.notification_type}
                />
            </Draggable>
        );
    };

    const foldersWithTopics = folders.map((folder) => {
        const filteredTopics = topics.filter((topic) => topic.folder === folder._id);

        return (
            <TopicFolder
                key={folder._id}
                folder={folder}
                index={folders.indexOf(folder)}
                topics={filteredTopics}
                folderPopover={folderPopover}
                toggleFolderPopover={toggleFolderPopover}
                saveFolder={saveFolder}
                deleteFolder={deleteFolder}
                opened={openedFolders[folder._id] ?? false}
                setOpened={(val) => {
                    setOpenedFolders({
                        ...openedFolders,
                        [folder._id]: val,
                    });
                }}
            >
                {filteredTopics.map((topic) => renderTopic(topic))}
            </TopicFolder>
        );
    });

    const topicsWithoutFolder = topics.filter((topic) => topic.folder == null).map((topic) => renderTopic(topic));

    const sensors = useCustomSensors({activationConstraint: {distance: 10}});

    /** a reference element is needed for finding first scrollable parent */
    const referenceElement = createRef<HTMLDivElement>();

    const scrollRestore = useScrollRestore(referenceElement);

    return (
        <>
            <DndContext
                sensors={sensors}
                autoScroll={{
                    // by default it looks for an element to scroll in order of appearance in the DOM starting from window
                    // in our case with many absolutely positioned modal-like views it works better to reverse the order
                    // so it starts with scrollable element and goes up the DOM tree.
                    order: TraversalOrder.ReversedTreeOrder,
                }}
                onDragMove={() => {
                    scrollRestore.savePosition();
                }}
                onDragEnd={(event) => {
                    scrollRestore.restoreSavedPosition();

                    const topicId: ITopic['_id'] = event.active.id.toString();

                    if (topicId == null || event.over == null) {
                        return;
                    }

                    const folderId: ITopicFolder['_id'] = event.over.id.toString();
                    const folder = folders.find((folder) => folder._id === folderId) ?? null;

                    moveTopic(topicId, folder).then(() => {
                        if (folder != null) {
                            setOpenedFolders({
                                ...openedFolders,
                                [folder._id]: true,
                            });
                        }
                    });


                }}
            >
                {foldersWithTopics}
                {topicsWithoutFolder}

                {/** https://docs.dndkit.com/api-documentation/draggable/drag-overlay */}
                <Overlay
                    component={({id}) => {
                        const topic = topics.find((topic) => topic._id === id);

                        if (topic == null) {
                            throw new Error('topic is null');
                        }

                        const subscription = topic.subscribers?.find((sub) => sub.user_id === user._id);

                        return (
                            <Topic
                                topic={topic}
                                actions={actions}
                                users={users}
                                selected={selectedTopicId === topic._id}
                                subscriptionType={subscription?.notification_type}
                            />
                        );
                    }}
                />
            </DndContext>

            <div ref={referenceElement} />
        </>
    );
};

export default TopicList;
