import React, {useCallback, useEffect} from 'react';
import {Popover, PopoverBody} from 'reactstrap';
import {ITopicFolder} from 'interfaces/topic';

interface IProps {
    folder: ITopicFolder;
    toggleFolderPopover: (folder: ITopicFolder) => void;
    folderPopover: string;
    actions: Array<any>;
    buttonRef: React.MutableRefObject<any>;
    index: number;
}

export function TopicFolderActions({folder, toggleFolderPopover, folderPopover, actions, buttonRef, index}: IProps) {
    const elem = document.querySelectorAll('.simple-card__group-header-actions')[index];

    const toggle = useCallback((e) => {
        if (!elem?.contains(e.target)) {
            toggleFolderPopover(folder);
        }
    }, []);

    useEffect(() => {
        document.addEventListener('click', toggle);

        return () => {
            document.removeEventListener('click', toggle);
        };
    });

    return (
        <Popover
            key={'popover-folder-' + folder._id}
            isOpen={folderPopover === folder._id}
            target={buttonRef}
            className="action-popover"
            delay={0}
            fade={false}
        >
            <PopoverBody>
                {
                    actions.map((action: any) => (
                        <button key={action.id}
                            type="button"
                            className="dropdown-item"
                            onClick={(e) => {
                                toggle(e);
                                action.callback();
                            }}
                        >
                            <i className={'icon--' + action.icon} />
                            {action.name}
                        </button>
                    ))
                }
            </PopoverBody>
        </Popover>
    );
}
