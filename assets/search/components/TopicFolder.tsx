/* eslint-disable react/prop-types */
import React, {useState, useRef} from 'react';
import {gettext} from 'utils';
import classNames from 'classnames';
import {TopicFolderEditor} from './TopicFolderEditor';
import {TopicFolderActions} from './TopicFolderActions';
import {ITopicFolder} from 'interfaces';

const EDITING_OFF = 0;
const EDITING_ON = 1;
const EDITING_ERROR = 2;

interface IProps {
    folder: ITopicFolder;
    topics: any;
    folderPopover: string;
    toggleFolderPopover: (folder: any) => void;
    moveTopic: any;
    saveFolder: any;
    deleteFolder: any;
    children: any;

    /**
     * Used to track the order of every topic folder
     * so that when open, the actions popover gets attached
     * to the correct element from the DOM
     */
    index: number;
}

export function TopicFolder({
    folder,
    topics,
    folderPopover,
    toggleFolderPopover,
    moveTopic,
    saveFolder,
    deleteFolder,
    children,
    index,
}: IProps) {
    const [opened, setOpened] = useState(false);
    const [editing, setEditing] = useState(EDITING_OFF);
    const [dragover, setDragOver] = useState(false);
    const buttonRef = useRef(null);

    const actions = [
        {
            id: 'edit',
            name: gettext('Rename'),
            icon: 'edit',
            callback: () => setEditing(EDITING_ON),
        },
        {
            id: 'delete',
            name: gettext('Delete'),
            icon: 'trash',
            callback: () => {
                deleteFolder(folder);
                toggleFolderPopover(folder);
            },
        },
    ];

    return (
        <div
            key={folder._id}
            className="simple-card__group"
            data-test-id={`folder-card--${folder.name}`}
            onDragOver={(event) => {
                event.preventDefault();
                event.dataTransfer.dropEffect = 'move';
                setDragOver(true);
            }}
            onDragLeave={() => {
                setDragOver(false);
            }}
            onDrop={(event) => {
                const topic = event.dataTransfer.getData('topic');

                setDragOver(false);
                moveTopic(topic, folder).then(() => {
                    if (!opened) {
                        setOpened(true);
                    }
                });
            }}
        >
            {editing ? (
                <TopicFolderEditor
                    folder={folder}
                    error={editing === EDITING_ERROR ? {} : null}
                    onSave={(name) => {
                        saveFolder(folder, {name})
                            .then(() => setEditing(EDITING_OFF), () => setEditing(EDITING_ERROR));
                    }}
                    onCancel={() => setEditing(EDITING_OFF)}
                />
            ) : (
                <div className={classNames('simple-card__group-header', {
                    'simple-card__group-header--ondragover': dragover,
                })}>
                    {opened ? (
                        <button
                            type="button"
                            className="icon-button icon-button--tertiary"
                            title={gettext('Close')}
                            onClick={() => setOpened(false)}
                        ><i className="icon--minus"></i></button>
                    ) : (
                        <button
                            type="button" className="icon-button icon-button--tertiary"
                            title={gettext('Open')}
                            onClick={() => setOpened(true)}
                            disabled={topics.length === 0}
                        ><i className="icon--plus"></i></button>
                    )}
                    <div className="simple-card__group-header-title">
                        <i className="icon--folder"></i>
                        <span className="simple-card__group-header-name">{folder.name}</span>
                    </div>
                    <span className={classNames('badge rounded-pill me-2', {
                        'badge--neutral': topics.length > 0,
                        'badge--neutral-translucent': topics.length === 0,
                    })}>{topics.length}</span>
                    <div className="simple-card__group-header-actions">
                        <button
                            onClick={() => {
                                toggleFolderPopover(folder);
                            }}
                            ref={buttonRef}
                            className="icon-button icon-button--tertiary"
                            aria-label={gettext('Folder Actions')}>
                            <i className='icon--more'></i>
                        </button>
                        {
                            folderPopover == folder._id && (
                                <TopicFolderActions
                                    index={index}
                                    buttonRef={buttonRef}
                                    actions={actions}
                                    folder={folder}
                                    folderPopover={folderPopover}
                                    toggleFolderPopover={toggleFolderPopover}
                                />
                            )
                        }
                    </div>
                </div>
            )}
            {opened && (
                <div className="simple-card__group-content">
                    {children}
                </div>
            )}
        </div>
    );
}


