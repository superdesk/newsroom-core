import React, {useState, useRef, useEffect, createRef} from 'react';
import {get} from 'lodash';
import {DndContext, TraversalOrder, getScrollableAncestors} from '@dnd-kit/core';

import {ITopicAction, Topic} from './Topic';
import {TopicFolder} from './TopicFolder';
import {ITopic, ITopicFolder, IUser} from 'interfaces';

import {Draggable} from '../../components/drag-and-drop/draggable';
import {Overlay} from 'components/drag-and-drop/overlay';
import {useCustomSensors} from 'components/drag-and-drop/use-custom-sensors';

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
    const scrollableParent = useRef<Element>();
    const lastScrollPosition = useRef<number | null>(0); // of scrollable parent

    /** a reference element is needed for finding first scrollable parent */
    const referenceElement = createRef<HTMLDivElement>();

    useEffect(() => {
        scrollableParent.current = getScrollableAncestors(referenceElement.current)[0];
    }, []);

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
                    // remember scroll position
                    lastScrollPosition.current = scrollableParent.current?.scrollTop ?? null;
                }}
                onDragEnd={(event) => {
                    setTimeout(() => {
                        /**
                         * Restore last scroll position in case auto-scrolling was performed while dragging.
                         * Without this, after scrolling and dropping, scroll jumps to position as if no scrolling happened.
                         * I suspect it might be because `moveTopic` is async, the dragging library might assume that dropping was cancelled.
                         */
                        if (scrollableParent.current != null && lastScrollPosition.current != null) {
                            scrollableParent.current.scrollTop = lastScrollPosition.current;
                        } else {
                            // reset last scroll position
                            lastScrollPosition.current = scrollableParent.current?.scrollTop ?? null;
                        }
                    });

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
